from functools import lru_cache
from typing import Dict, List, Tuple

from .base import NonogramSolver

ROW = 0
COLUMN = 1
EMPTY = 0
FILLED = 1


@lru_cache(maxsize=256)
def _generate_line_possibilities(
        clues: Tuple[int, ...], length: int
) -> List[List[int]]:
        """
        Generate all possible line configurations for given clues.
        Memoized to avoid regenerating for identical clue patterns.

        Args:
                clues: Tuple of clue values (e.g., (2, 3, 1) means blocks of 2, 3, and 1 filled cells)
                length: Total length of the line

        Returns:
                List of all valid possibilities for this line
        """
        possibilities = []

        # empty clues case; line would be empty, only 1 possibility
        if not clues or all(clue == 0 for clue in clues):
                return [[EMPTY] * length]

        # Calculate filled blocks and remaining space
        filled_blocks = [[FILLED] * clue for clue in clues]
        total_filled = sum(clues)
        min_gaps = len(clues) - 1  # Minimum gaps between blocks
        remaining_space = length - total_filled - min_gaps

        if remaining_space < 0:
                return []  # Impossible configuration

        # Number of slots for distributing remaining empty cells
        # (before first block, between blocks, after last block)
        num_slots = len(clues) + 1

        # Generate all ways to distribute remaining_space empties across num_slots
        # This uses "stars and bars" via itertools
        for distribution in _distribute_empties(remaining_space, num_slots):
                # Build the line configuration
                possibility = []

                # Add empties before first block
                possibility.extend([EMPTY] * distribution[0])

                # Add filled blocks with gaps
                for i, block in enumerate(filled_blocks):
                        possibility.extend(block)
                        if i < len(filled_blocks) - 1:
                                # Required gap + optional empties
                                gap_size = 1 + distribution[i + 1]
                                possibility.extend([EMPTY] * gap_size)

                # Add empties after last block
                possibility.extend([EMPTY] * distribution[-1])

                possibilities.append(possibility)

        return possibilities


@lru_cache(maxsize=512)
def _distribute_empties(m: int, k: int) -> Tuple[Tuple[int, ...], ...]:
        """
        Distribute m empty cells across k slots.
        Memoized recursive approach.

        This generates all non-negative integer solutions to x1 + x2 + ... + xk = m

        Args:
                m: Number of empty cells to distribute
                k: Number of slots

        Returns:
                Tuple of tuples, each representing one distribution (tuples for hashability)
        """
        if k == 1:
                return ((m,),)

        if m == 0:
                return (tuple([0] * k),)

        results = []

        # For each possible value in the first slot (0 to m)
        for first_slot in range(m + 1):
                # Recursively distribute the remaining (m - first_slot) across (k - 1) slots
                for rest in _distribute_empties(m - first_slot, k - 1):
                        results.append((first_slot,) + rest)

        return tuple(results)


class line:
        """
        Class structure to define a line (row/column).
        Attributes:
                - type (int): ROW (0) or COLUMN (1).
                - lenght (int): the length of this line.
                - index (int): "which row/column is this in the puzzle?".
                - clues (list[int]): starting clues to generate possibilities for this line.
                - possibilities (list[list[int]]): possibilities for this line; will shrink as constraints propagate.
        """

        def __init__(
                self,
                type: int,
                length: int,
                index: int,
                clues: List[int],
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
                Returns the list of all possible configurations for this line based on its clues.
                """
                # Use memoization for repeated clue patterns
                self.possibilities = _generate_line_possibilities(
                        tuple(self.clues), self.length
                )
                return

        def prune(self, constraints: List, *prePossCount: int):
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
                                if constraints[i] is None:
                                        continue
                                elif possibility[i] != constraints[i]:
                                        valid = False
                                        break
                        if valid:
                                newPossibilities.append(possibility)
                self.possibilities = newPossibilities

        def perpendicular(self, lines: Dict, processingQueue: List):
                """
                Returns list of propagated perpendicular lines (list[processingEntry])
                """

                # I don't think a line can have 0 possibilities, but just in case
                if not self.possibilities:
                        print("Line has 0 possibility! Skipping perpendicular check...")
                        return

                # TODO: is this even correct?
                # finds bits that stay the same in remaining possibilities
                perpLines = []
                checker = self.possibilities[0][:]  # shallow copy is sufficient

                if len(self.possibilities) >= 2:
                        for possibility in self.possibilities[1:]:
                                for i in range(len(checker)):
                                        if checker[i] == possibility[i]:
                                                continue  # FILLED==FILLED or EMPTY==EMPTY
                                        checker[i] = None  # type: ignore

                # find possible processing queue entries
                key = "columns" if self.type == ROW else "rows"
                lineLst: List[line] = lines[key]
                for i in range(len(checker)):
                        if checker[i] in (EMPTY, FILLED):
                                perpLine = lineLst[i]
                                if len(perpLine.possibilities) == 1:
                                        continue  # skip solved lines
                                constraint = [None for _ in range(perpLine.length)]
                                constraint[self.index] = checker[i]  # type: ignore

                                newEntry = processingEntry(perpLine, constraint)
                                perpLines.append(newEntry)

                for entry in perpLines:
                        entry.printEntry()

                # from candidate lines:
                # if line solved, don't add to queue at all
                # if line alr in queue, merge entry, else put entry to queue
                for entry in perpLines:
                        alreadyInQueue = False
                        for existingEntry in processingQueue:  # this for loop is the entire reason why processingQueue uses a list lol
                                if entry.line == existingEntry.line:
                                        existingEntry.mergeEntry(entry)
                                        alreadyInQueue = True
                                        break
                        if not alreadyInQueue:
                                processingQueue.append(entry)


class processingEntry:
        def __init__(self, line: line, constraint: List):
                self.line = line
                self.constraint = constraint

        def mergeEntry(self, other):
                # preprequisite for merging
                if self.line == other.line:
                        # assumptions: the 2 constraints don't have overlaps in each element
                        mergedConstraint = []
                        for thisBit, thatBit in zip(
                                self.constraint,
                                other.constraint,
                        ):
                                if thisBit in (FILLED, EMPTY):
                                        mergedConstraint.append(thisBit)
                                elif thatBit in (FILLED, EMPTY):
                                        mergedConstraint.append(thatBit)
                                else:
                                        mergedConstraint.append(None)
                        self.constraint = mergedConstraint

        def printEntry(self):
                pass


class CSPSolver(NonogramSolver):
        name = "CSP Solver"
        description = (
                "Solver modeling the puzzle as a Constrained Satisfaction Problem."
        )

        def _solve_internal(self):
                """
                Constraint Satisfaction Problem (CSP) solver for nonogram puzzles.

                This algorithm models the nonogram as a CSP where each row and column is a constraint
                that must be satisfied. It uses constraint propagation to systematically eliminate
                invalid possibilities without backtracking.

                Returns:
                    list[list[int]]: 2D grid solution (1=filled, 0=empty), or None if failed
                """
                try:
                        # formats the puzzle into rows and columns
                        lines = {"rows": [], "columns": []}
                        R, C = lines["rows"], lines["columns"]
                        for i in range(self.height):
                                newRow = line(
                                        type=ROW,
                                        length=self.width,
                                        index=i,
                                        clues=self.rows[i],
                                )
                                newRow.generatePossibilities()
                                R.append(newRow)
                        for i in range(self.width):
                                newColumn = line(
                                        type=COLUMN,
                                        length=self.height,
                                        index=i,
                                        clues=self.columns[i],
                                )
                                newColumn.generatePossibilities()
                                C.append(newColumn)

                        # greedy ordering (in terms of possibilities count per line) + queue to determine what to process next
                        greedyOrdering = []

                        def greedyEntrySort(
                                entries: List,
                                entryType: int,
                        ):
                                count = self.height if entryType == ROW else self.width
                                lines = R if entryType == ROW else C
                                for ptr in range(count):
                                        entries.append((entryType, ptr))
                                entries.sort(
                                        key=lambda entry: len(
                                                lines[entry[1]].possibilities
                                        )
                                )

                                return entries

                        entriesR = greedyEntrySort([], ROW)
                        entriesC = greedyEntrySort([], COLUMN)

                        ptrR, ptrC = 0, 0
                        while ptrR < len(entriesR) and ptrC < len(entriesC):
                                idxR, idxC = entriesR[ptrR][1], entriesC[ptrC][1]
                                possCountR, possCountC = (
                                        len(R[idxR].possibilities),
                                        len(C[idxC].possibilities),
                                )
                                if possCountR <= possCountC:
                                        greedyOrdering.append(entriesR[ptrR])
                                        ptrR += 1
                                else:
                                        greedyOrdering.append(entriesC[ptrC])
                                        ptrC += 1
                        if ptrR < len(entriesR):
                                ptr = ptrR
                                entries = entriesR
                        else:
                                ptr = ptrC
                                entries = entriesC
                        while ptr < len(entries):
                                greedyOrdering.append(entries[ptr])
                                ptr += 1

                        greedyOrdering = tuple(greedyOrdering)

                        processingQueue: List[
                                processingEntry
                        ] = []  # effectively a queue, with pop(0) and append()

                        def printQueue(processingQueue: List[processingEntry]):
                                pass

                        for entryType, entryIndex in greedyOrdering:
                                key = "columns" if entryType == COLUMN else "rows"
                                initLine: line = lines[key][entryIndex]
                                initLine.perpendicular(lines, processingQueue)
                        printQueue(processingQueue)

                        # regular workflow to induce propagation
                        while len(processingQueue) > 0:
                                currEntry: processingEntry = processingQueue.pop(0)
                                currLine: line = currEntry.line
                                currConstraint: List = currEntry.constraint

                                if len(currLine.possibilities) <= 1:
                                        continue

                                # in case prune() doesn't prune anything
                                prePossCount = len(currLine.possibilities)

                                # remove invalid possibilities based on constraint
                                currLine.prune(currConstraint, prePossCount)

                                if len(currLine.possibilities) == prePossCount:
                                        pass

                                currLine.perpendicular(lines, processingQueue)

                        # by this point in the program, all lines should only have 1 possibility: their solution
                        solution = []
                        for i, row in enumerate(R):
                                if len(row.possibilities) == 0:
                                        print(f"Row {i} has no possibilities!")
                                elif len(row.possibilities) > 1:
                                        print(
                                                f"Row {i} has {len(row.possibilities)} possibilities! You may need some backtracking as fallback."
                                        )
                                else:
                                        solution.append(row.possibilities[0])

                        # don't forget to do this lol
                        self.grid = solution

                        return self.grid

                except Exception as e:
                        print(f"Exception occurred: {type(e).__name__}: {e}")
