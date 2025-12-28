from multiprocessing import process
from .base import NonogramSolver
from enum import Enum
import copy
from queue import Queue

class CSPSolver(NonogramSolver):
    name = "CSP Solver"
    description = "Solver modeling the puzzle as a Constrained Satisfaction Problem."

    def _solve_internal(self):
        # Instance variables are ready to use:
        # self.width, self.height, self.rows, self.columns, self.grid
        """

        *\n
        Models a nonogram puzzle as a Constraint Satisfaction Problem.\n
        Call each row/column a line.\n
        With each line's clues, generate all possibilities for it.\n
        As more constraints are declared, they wiil propagate to numerous lines and reduce the possiblities, eventually leaving behind the solution.\n

        *\n
        Sort the lines by number of possibilities, increasing.\n
        This will be our greedy heuristics to check which lines need to be checked and created constraints out of first.\n
        Call this the "priority" of checking lines.\n

        *\n
        A queue of lines to check next should be created.\n
        When we check each line, they need to have additional constraints, for possibilities elimination; a dict works great for this.\n
        On initialization of it, add all rows and columns to the queue, with no additional constraint.\n
        Pop the head of the queue when looking for the next line to check.\n

        *\n
        When checking a line:\n
        1. From clues + additional constraints, remove all invalid possibilities.
        2. From the remaining possibilities, identify which bits (1 OR 0) are the same across all of them.
            These bits act as additional constraints (because they MUST stay the same).
            Each of them identifies a cell on the nonogram puzzle, and we consider the perpendicular line to our current line, at that cell.
        3. List all perpendicular lines that needs additional constraints added to them, by priority.
        4. Remove lines that are already solved. Add the remaining ones to the tail of the queue. This is effectively how we will "solve" the puzzle.
        5. If a line is already in the queue, add additional constraints to them instead of a new queue entry.
        """
        ROW = 0
        COLUMN = 1
        EMPTY = 0
        FILLED = 1

        class line():
            """
            Class structure to define a line (row/column).\n
            Attributes:
                - type (int): ROW (0) or COLUMN (1).
                - lenght (int): the length of this line.
                - index (int): "which row/column is this in the puzzle?".
                - clues (list[int]): starting clues to generate possibilities for this line.
                - possibilities (list[list[int]]): possibilities for this line; will shrink as constraints propagate.
            """
            def __init__(self,
                type: int,
                length: int,
                index: int,
                clues: list[int]
            ):
                self.type = type
                self.length = length
                self.index = index
                self.clues = clues
                self.possibilities = []

            def __eq__(self, other):
                return self.type == other.type & self.index == other.index

            def generatePossibilities(self):
                """
                Only called once for each new line.\n
                possibilty format: list[int]
                """
                # The clues tell us there must be these blocks of FILLEDs in our line
                filledBlocks = []
                remainingBits = self.length
                for clue in self.clues:
                    filledBlocks.append([FILLED for _ in range(clue)])
                    remainingBits -= clue

                # and between them are blocks that either can have EMPTYs or nothing at all
                # Of course, between any 2 consecutive FILLED blocks, there must be
                # at least 1 EMPTY
                emptyRequired = []
                for _ in range(len(filledBlocks)):
                    emptyRequired.append([EMPTY])
                    remainingBits -= 1
                emptyRequired.append([]) # at the end
                emptyRequired.insert(0, []) # at the beginning
                slots = len(emptyRequired)

                # Consider the bits left over after filling in the required EMPTYs
                emptyOptional = []
                def emptyMBitsInKSlots(
                    m: int,
                    k: int,
                    current: list,
                    emptyOptional: list
                ):
                    if k == 1: # base case
                        current.append([EMPTY] * m)
                        # after this, no more EMPTYs to append
                        emptyOptional.append(copy.deepcopy(current))
                        # backtrack
                        current.pop()
                        return
                    else: # normal case
                        for i in range(m+1):
                            current.append([EMPTY] * i)
                            emptyMBitsInKSlots(m-1,k-1,current, emptyOptional)
                            # backtrack
                            current.pop()
                emptyMBitsInKSlots(remainingBits, slots, [], emptyOptional)

                # NOW we're actually creating blocks of EMPTYs or nothing
                mergedEmpties = []
                for constructorOptional in emptyOptional:
                    merged = []
                    for required, optional in zip(emptyRequired, constructorOptional):
                        merged.append(required + optional)
                    mergedEmpties.append(merged)

                # and finally, weave the EMPTY and FILLED blocks together
                for constructorEmpty in mergedEmpties: # dude why am i writing like it's java lol
                    nested = []
                    for filled, empty in zip(filledBlocks, constructorEmpty[:-1:]):
                        nested.append(empty)
                        nested.append(filled)
                    nested.append(constructorEmpty[-1])

                    def flatten(
                        lst: list
                    ):
                        result = []
                        for element in lst:
                            if not isinstance(element, list):
                                result.append(element)
                            else:
                                if len(element) == 0: continue
                                result.extend(flatten(element))
                        return result

                    possibility = flatten(nested)
                    self.possibilities.append(possibility)

            def prune(self,
                      constraints: list
            ):
                """
                Remove invalid possibilities of a line based on constraints.\n
                expected constraint format:\n
                    - example: line, self.length = 4\n
                    - element at index 0 must be EMPTY, at index 3 must be FILLED\n
                => constraint = [EMPTY, None, None, FILLED]
                """
                newPossibilities = []
                for possibility in self.possibilities:
                    valid = True
                    for i in range(self.length):
                        if constraints[i] is None: continue
                        elif possibility[i] != constraints[i]:
                            valid = False
                            break
                    if valid: newPossibilities.append(possibility)
                self.possibilities = newPossibilities

            def perpendicular(self,
                lines: dict,
                processingQueue: list):
                """
                Returns list of propagated perpendicular lines (list[processingEntry])
                """
                # finds bits that stay the same in remaining possibilities
                perpLines = []
                checker = self.possibilities[0]

                if len(self.possibilities) > 1:
                    for possibility in self.possibilities[1:]:
                        for i in range(len(checker)):
                            if checker[i] == possibility[i]: continue # FILLED==FILLED or EMPTY==EMPTY
                            checker[i] == None

                # find possible processing queue entries
                key = "columns" if self.type == ROW else "row"
                lineLst: list[line] = lines[key]
                for i in range(checker):
                    if checker[i] in (EMPTY, FILLED):
                        perpLine = lineLst[i]
                        if len(perpLine.possibilities) == 1: continue # skip solved lines
                        constraint = [None for _ in range(perpLine.length)]
                        constraint[self.index] = checker[i]

                        newEntry = processingEntry(perpLine, constraint)
                        perpLines.append(newEntry)
                return perpLines

        # main solution!

        # formats the puzzle into rows and columns
        lines = {
            "rows": [],
            "columns": []
        }
        R, C = lines["rows"], lines["columns"]
        for i in range(self.height):
            newRow = line(
                type=ROW,
                length=self.width,
                index=i,
                clues=self.rows[i]
            )
            newRow.generatePossibilities()
            R.append(newRow)
        for i in range(self.width):
            newColumn = line(
                type=COLUMN,
                length=self.height,
                index=i,
                clues=self.columns
            )
            newColumn.generatePossibilities()
            C.append(newColumn)

        # greedy ordering + queue to determine what to process next
        greedyOrdering = []
        ptrR, ptrC = 0, 0
        while ptrR < self.height & ptrC < self.width:
            possCountR, possCountC = len(R[ptrR].possibilities), len(C[ptrC].possibilities)
            if possCountR <= possCountC:
                entryType, entryIndex = ROW, ptrR
                greedyOrdering.append((entryType, entryIndex))
                ptrR += 1
            else:
                entryType, entryIndex = COLUMN, ptrC
                greedyOrdering.append((entryType, entryIndex))
                ptrC += 1
        if ptrC > self.height:
            while ptrC < self.width: greedyOrdering.append((COLUMN, ptrC))
        else:
            while ptrR < self.height: greedyOrdering.append((ROW, ptrR))
        greedyOrdering = tuple(greedyOrdering)

        class processingEntry():
            def __init__(self,
                line: line,
                constraint: list
            ):
                self.line = line
                self.constraint = constraint

            def mergeEntry(self, other):
                # preprequisite for merging
                if self.line == other.line:
                    # assumptions: the 2 constraints don't have overlaps in each element
                    mergedConstraint = []
                    for thisBit, thatBit in zip(self.constraint, other.constraint):
                        if thisBit in (FILLED, EMPTY): mergedConstraint.append(thisBit)
                        elif thatBit in (FILLED, EMPTY): mergedConstraint.append(thatBit)
                        else: mergedConstraint.append(None)
                    self.constraint = mergedConstraint

        processingQueue: list[processingEntry] = [] # effectively a queue, with pop(0) and append()
        # at start, add all elements in greedy order to queue, with no constraint
        for (entryType, entryIndex) in greedyOrdering:
            constraintLength = self.height if entryType == ROW else self.width
            processingQueue.append(
                processingEntry(R[entryIndex],
                                [None for _ in range(constraintLength)]
            ))
        # regular workflow to induce propagation
        while len(processingQueue) > 0:
            currEntry: processingEntry = processingQueue.pop(0)
            currLine: line = currEntry.line
            currConstraint: list = currEntry.constraint

            # remove invalind possibilities based on constraint
            currLine.prune(currConstraint)

            # from the remaining possibilities, find propagated perpendicular lines
            perpLines: list[processingEntry] = currLine.perpendicular(lines, processingQueue)
            # if line alr in queue, merge entry, else put entry to queue
            for entry in perpLines:
                alreadyInQueue = False
                for existingEntry in processingQueue: # this for loop is the entire reason why processingQueue uses a list lol
                    if entry.line == existingEntry.line: existingEntry.mergeEntry(entry)
                    alreadyInQueue = True
                    break
                if not alreadyInQueue: processingQueue.append(entry)

        # by this point in the program, all lines should only have 1 possibility: their solution
        solution = []
        for row in R:
            solution.append(row.possibilities[0])

        # don't forget to do this lol
        self.grid = solution
        return self.grid