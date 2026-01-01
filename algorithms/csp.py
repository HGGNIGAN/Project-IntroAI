from .base import NonogramSolver
import copy
import time
import logging
import os

proj_dir = os.path.dirname(os.path.dirname(__file__))
log_path = os.path.join(proj_dir, "temp", "trace.log")

logging.basicConfig(
    # CHANGE THIS TO A HIGHER LEVEL IF NOT DEBUGGING
    level=logging.INFO,
    filename=log_path,
    filemode='w',
    format="[%(levelname)s]: %(message)s"
)
logger = logging.getLogger(__name__)
longbreak = "-" * 50

class CSPSolver(NonogramSolver):
    name = "CSP Solver"
    description = "Solver modeling the puzzle as a Constrained Satisfaction Problem. Only partially complete, by design."

    def _solve_internal(self):
        """
        Constraint Satisfaction Problem (CSP) solver for nonogram puzzles.

        This algorithm models the nonogram as a CSP where each row and column is a constraint
        that must be satisfied. It uses constraint propagation to systematically eliminate
        invalid possibilities without backtracking.

        Algorithm Overview:
        1. Generate all valid possibilities for each row/column constraint
        2. Apply greedy heuristic ordering (process lines with fewer possibilities first)
        3. Use constraint propagation to eliminate invalid possibilities:
           - When a cell is determined in one line, propagate to perpendicular lines
           - Remove possibilities that conflict with known cell values
        4. Repeat until no more deductions can be made

        Key Features:
        - Pure constraint propagation (no backtracking fallback)
        - Bidirectional constraint enforcement (rows ↔ columns)
        - Greedy constraint ordering for efficiency
        - Intersection-based deduction (cells that are the same across all possibilities)

        Limitations:
        - May fail to solve puzzles requiring search/backtracking
        - Returns incorrect results if constraint propagation is insufficient
        - Considered "partially complete" by design

        Time Complexity: O(m × n × P) where P is average possibilities per constraint
        Space Complexity: O(m × n × P) for storing all possibilities

        Returns:
            list[list[int]]: 2D grid solution (1=filled, 0=empty), or None if failed
        """
        try:
            # Instance variables are ready to use:
            # self.width, self.height, self.rows, self.columns, self.grid
            logger.debug("Initial board state:")
            logger.debug(f"Size: {self.width}*{self.height}")
            logger.debug(f"Row clues: {self.rows}")
            logger.debug(f"Column clues: {self.columns}")
            logger.info(longbreak)

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
                    return self.type == other.type and self.index == other.index

                def generatePossibilities(self):
                    """
                    Only called once for each new line.\n
                    possibilty format: list[int]
                    """
                    logger.info(f"Generating possibilities for line type {self.type}, index {self.index}")
                    logger.debug(f"Clues: {self.clues}")
                    start_time = time.time()

                    # empty clues case; line would be empty, only 1 possibility
                    if not self.clues or all(clue == 0 for clue in self.clues):
                        self.possibilities.append([EMPTY] * self.length)

                    else:
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
                        for _ in range(len(filledBlocks)-1):
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
                                    emptyMBitsInKSlots(m-i,k-1,current, emptyOptional)
                                    # backtrack
                                    current.pop()
                        emptyMBitsInKSlots(remainingBits, slots, [], emptyOptional)


                        # NOW we're actually creating blocks of EMPTYs or nothing
                        mergedEmpties = []
                        for constructorOptional in emptyOptional:
                            merged = []
                            for required, optional in zip(emptyRequired, constructorOptional):
                                    merged_result = required + optional
                                    merged.append(merged_result)

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
                                        if len(element) == 0:
                                            continue
                                        result.extend(flatten(element))
                                return result

                            possibility = flatten(nested)

                            self.possibilities.append(possibility)

                    logger.debug(f"Generated {len(self.possibilities)} possibilities in {time.time() - start_time:.4f}s")
                    logger.debug("Possibilities:")
                    for possibility in self.possibilities:
                        logger.debug(f"  {possibility}")
                    logger.debug("")
                    return

                def prune(self,
                          constraints: list,
                          *prePossCount: int
                ):
                    """
                    Remove invalid possibilities of a line based on constraints.\n
                    expected constraint format:\n
                        - example: line, self.length = 4\n
                        - element at index 0 must be EMPTY, at index 3 must be FILLED\n
                    => constraint = [EMPTY, None, None, FILLED]
                    """
                    logger.info(f"Pruning line type={self.type}, index={self.index}")
                    start_time = time.time()
                    newPossibilities = []
                    for possibility in self.possibilities:
                        valid = True
                        for i in range(self.length):
                            if constraints[i] is None:
                                continue
                            elif possibility[i] != constraints[i]:
                                valid = False
                                break
                        if valid:
                            newPossibilities.append(possibility)
                    self.possibilities = newPossibilities

                    logger.debug(f"Pruned from {prePossCount[0] if prePossCount else "x"} to {len(self.possibilities)} possibilities in {time.time() - start_time:.4f}s")
                    for possibility in self.possibilities:
                        logger.debug(f"  {possibility}")
                    logger.info("")

                def perpendicular(self,
                    lines: dict,
                    processingQueue: list):
                    """
                    Returns list of propagated perpendicular lines (list[processingEntry])
                    """
                    logger.info(f"Finding propagating perpendicular lines of line type={self.type}, index={self.index}")
                    start_time = time.time()
                    # I don't think a line can have 0 possibilities, but just in case
                    if not self.possibilities:
                        logger.error("Line has 0 possibility! Skipping perpendicular check...")
                        return

                    # TODO: is this even correct?
                    # finds bits that stay the same in remaining possibilities
                    perpLines = []
                    checker = copy.deepcopy(self.possibilities[0])

                    if len(self.possibilities) >= 2:
                        for possibility in self.possibilities[1:]:

                            for i in range(len(checker)):
                                if checker[i] == possibility[i]:
                                    continue # FILLED==FILLED or EMPTY==EMPTY
                                checker[i] = None
                    logger.debug(f"Checker: {checker}")

                    # find possible processing queue entries
                    key = "columns" if self.type == ROW else "rows"
                    lineLst: list[line] = lines[key]
                    for i in range(len(checker)):
                        if checker[i] in (EMPTY, FILLED):
                            perpLine = lineLst[i]
                            if len(perpLine.possibilities) == 1:
                                continue # skip solved lines
                            constraint = [None for _ in range(perpLine.length)]
                            constraint[self.index] = checker[i]

                            newEntry = processingEntry(perpLine, constraint)
                            perpLines.append(newEntry)

                    logger.debug(f"Found {len(perpLines)} propagating perpendicular lines in {time.time() - start_time:.4f}s")
                    for entry in perpLines:
                        entry.printEntry()

                    # from candidate lines,
                    # if line solved, don't add to queue at all
                    # if line alr in queue, merge entry, else put entry to queue
                    logger.info("Merging/adding entries to processingQueue...")
                    for entry in perpLines:
                        alreadyInQueue = False
                        for existingEntry in processingQueue: # this for loop is the entire reason why processingQueue uses a list lol
                            if entry.line == existingEntry.line:
                                logger.debug(f"Merging constraint for line type={entry.line.type}, index={entry.line.index}")
                                existingEntry.mergeEntry(entry)
                                alreadyInQueue = True
                                break
                        if not alreadyInQueue:
                            logger.debug(f"Adding line type={entry.line.type}, index={entry.line.index} to queue")
                            processingQueue.append(entry)
                    logger.info("")

                    # return perpLines

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
                    clues=self.columns[i]
                )
                newColumn.generatePossibilities()
                C.append(newColumn)

            # greedy ordering (in terms of possibilities count per line) + queue to determine what to process next
            greedyOrdering = []

            logger.info("Soring rows and columns by greedy order (lines with fewer possibilities get preprocessed earlier)")
            def greedyEntrySort(
                entries: list,
                entryType: int,
            ):
                entryTypeStr = "rows" if entryType == ROW else "columns"
                logger.info(f"Sorting {entryTypeStr} with builtin sort() method")
                count = self.height if entryType == ROW else self.width
                lines = R if entryType == ROW else C
                for ptr in range(count):
                    entries.append((entryType, ptr))
                entries.sort(key=lambda entry: len(lines[entry[1]].possibilities))
                logger.debug(f"Sorted {entryTypeStr}: {entries}")
                return entries
            entriesR = greedyEntrySort([], ROW)
            entriesC = greedyEntrySort([], COLUMN)

            logger.debug("")
            logger.debug("Using double pointer method to append both entries lists to greedyOrdering...")
            ptrR, ptrC = 0, 0
            while ptrR < len(entriesR) and ptrC < len(entriesC):
                idxR, idxC = entriesR[ptrR][1], entriesC[ptrC][1]
                possCountR, possCountC = len(R[idxR].possibilities), len(C[idxC].possibilities)
                if possCountR <= possCountC:
                    logger.debug(f"Appending row {idxR} with {possCountR} possibilities to greedyOrdering")
                    greedyOrdering.append(entriesR[ptrR])
                    ptrR += 1
                else:
                    logger.debug(f"Appending column {idxC} with {possCountC} possibilities to greedyOrdering")
                    greedyOrdering.append(entriesC[ptrC])
                    ptrC += 1
            if ptrR < len(entriesR):
                logger.debug("There are remaining rows; appending to greedyOrdering")
                ptr = ptrR
                entries = entriesR
            else:
                logger.debug("There are remaining columns; appending to greedyOrdering")
                ptr = ptrC
                entries = entriesC
            while ptr < len(entries):
                entryTypeStr = "row" if entries[ptr][0] == ROW else "column"
                logger.debug(f"Appending {entryTypeStr} {entries[ptr][1]} to greedyOrdering")
                greedyOrdering.append(entries[ptr])
                ptr += 1

            greedyOrdering = tuple(greedyOrdering)
            logger.debug(f"greedyOrdering: {greedyOrdering}")
            logger.debug("")

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
                            if thisBit in (FILLED, EMPTY):
                                mergedConstraint.append(thisBit)
                            elif thatBit in (FILLED, EMPTY):
                                mergedConstraint.append(thatBit)
                            else:
                                mergedConstraint.append(None)
                        self.constraint = mergedConstraint

                def printEntry(self):
                    logger.debug(f"Entry type={self.line.type}, index={self.line.index}")
                    logger.debug(f"Constraints: {self.constraint}")

            processingQueue: list[processingEntry] = [] # effectively a queue, with pop(0) and append()
            def printQueue(processingQueue: list[processingEntry]):
                logger.debug("Processing Queue:")
                for entry in processingQueue:
                    logger.debug("**")
                    logger.debug(f"Entry type={entry.line.type}, index={entry.line.index}")
                    logger.debug(f"Constraint: {entry.constraint}")
                logger.debug("")


            logger.info("PREPROCESSING")
            logger.info(longbreak)
            for (entryType, entryIndex) in greedyOrdering:
                key = "columns" if entryType == COLUMN else "rows"
                initLine: line = lines[key][entryIndex]
                initLine.perpendicular(lines, processingQueue)
            logger.info("")
            logger.debug("processingQueue preload:")
            printQueue(processingQueue)

            # regular workflow to induce propagation
            logger.info("START PROCESSING")
            logger.info(longbreak)
            while len(processingQueue) > 0:
                currEntry: processingEntry = processingQueue.pop(0)
                currLine: line = currEntry.line
                currConstraint: list = currEntry.constraint

                if len(currLine.possibilities) <= 1:
                    logger.info(f"Skipping already solved line type={currLine.type}, index={currLine.index}")
                    logger.info(longbreak)
                    continue

                logger.info(f"Processing line type={currLine.type}, index={currLine.index}")
                logger.debug(f"Constraint: {currConstraint}")

                # in case prune() doesn't prune anything
                prePossCount = len(currLine.possibilities)

                # remove invalid possibilities based on constraint
                currLine.prune(currConstraint, prePossCount)

                if len(currLine.possibilities) == prePossCount:
                    logger.debug("Line's possibilities unpruned")

                currLine.perpendicular(lines, processingQueue)

                logger.info(longbreak)
            # by this point in the program, all lines should only have 1 possibility: their solution

            logger.info("Creating solution....")
            solution = []
            for i, row in enumerate(R):
                if len(row.possibilities) == 0:
                    logger.error(f"Row {i} has no possibilities!")
                elif len(row.possibilities) > 1:
                    logger.error(f"Row {i} has {len(row.possibilities)} possibilities! You may need some backtracking as fallback.")
                else:
                    logger.debug(f"Row {i}: {row.possibilities[0]}")
                    solution.append(row.possibilities[0])

            # don't forget to do this lol
            logger.info("Setting self.grid...")
            self.grid = solution
            logger.info("Returning self.grid...")
            return self.grid

        except Exception as e:
            logger.exception(f"Exception occurred: {type(e).__name__}: {e}")
            # logger.exception("Full traceback:")
            # traceback.print_exc()
            # raise


