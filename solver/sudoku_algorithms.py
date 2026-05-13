from ortools.sat.python import cp_model
from itertools import product


class SudokuSolver:
    """
    Solver for 9x9 Sudoku puzzles.
    
    Supports three approaches:
    1. Backtracking for standard recursive solving.
    2. Algorithm X / exact cover for efficient constraint-based solving.
    3. OR-Tools CP-SAT for puzzles with uncertain cells and ranked candidate digits.
    """
    def __init__(self, sudoku_board):
        self.sudoku_board = sudoku_board
    
    def is_valid(self, row_idx: int, col_idx: int, value: int) -> bool:
        """
        Check if assigning a value to an empty cell breaks the sudoku properties 
        each row, each column, and each 3 by 3 square has all the digits from 1-9
        """
        # Check if value is already in a row
        if any(cell == value for cell in self.sudoku_board[row_idx]):
            return False

        # Check if value is already in a column
        if any(self.sudoku_board[r][col_idx] == value for r in range(9)):
            return False

        # Check the 3 by 3 square
        r_0 = (row_idx // 3) * 3
        c_0 = (col_idx // 3) * 3
        for r in range(r_0, r_0 + 3):
            for c in range(c_0, c_0 + 3):
                if self.sudoku_board[r][c] == value:
                    return False
        return True

    def backtrack(self):
        """
        Solve the sudoku puzzle by using a backtracking algorithm
        """
        for row_idx, col_idx in product(range(9), range(9)):
            if self.sudoku_board[row_idx][col_idx] is None:
                for value in range(1, 10):
                    if self.is_valid(row_idx, col_idx, value):                
                        self.sudoku_board[row_idx][col_idx] = value
                        if self.backtrack():
                            return True
                        self.sudoku_board[row_idx][col_idx] = None
                return False
        return True
    
    @classmethod
    def build_cover_cols(cls, N: int = 9):
        cover_cols = ([("cell", r, c) for r, c in product(range(N), range(N))] +
         [("row", r ,n) for r, n in product(range(N), range(1, N + 1))] +
         [("col", c ,n) for c ,n in product(range(N), range(1, N + 1))] +
         [("box", b, n) for b, n in product(range(N), range(1, N + 1))])
    
        return cover_cols

    @classmethod
    def candidates(cls, N:int = 9):
        for r in range(N):
            for c in range(N):
                for d in range(1, N + 1):
                    yield (r,c,d)

    @staticmethod
    def cover_cols_satisfied(r: int, c:int, d:int):
        # Check which cover columns are satisfied by placing digit d at row r and column c

        # Get box index beloning to row r and column c
        b = (r // 3) * 3 + (c // 3) 

        return (("cell", r, c), ("row", r, d), ("col", c, d), ("box", b, d))

    @classmethod
    def build_cover_maps(cls):

        contraints_cols = cls.build_cover_cols()
        #print(f"Constraints cols: {contraints_cols}")

        constraints_to_candidates = {col: set() for col in contraints_cols}

        candidates_to_constraints = {}

        for rcd in cls.candidates():
            cols = cls.cover_cols_satisfied(*rcd)
            candidates_to_constraints[rcd] = cols
            for col in cols:
                constraints_to_candidates[col].add(rcd)

        return constraints_to_candidates, candidates_to_constraints

    @classmethod
    def select(cls, constraints_to_candidates: dict[tuple, dict[tuple]], candidates_to_constraints: dict[tuple, tuple[tuple]], chosen):

        removed = []
        for col in candidates_to_constraints[chosen]:
            if col not in constraints_to_candidates:
                continue
            for rcd in list(constraints_to_candidates[col]):
                for other_col in candidates_to_constraints[rcd]:
                    if other_col != col and other_col in constraints_to_candidates:
                        constraints_to_candidates[other_col].discard(rcd)
            removed.append((col, constraints_to_candidates.pop(col)))
        return removed

    @classmethod
    def deselect(cls, constraints_to_candidates: dict[tuple: dict[tuple]], candidates_to_constraints: dict[tuple: tuple[tuple]], removed):
        for col, rows in reversed(removed):
            constraints_to_candidates[col] = rows
            for rcd in rows:
                for other_col in candidates_to_constraints[rcd]:
                    if other_col != col and other_col in constraints_to_candidates:
                        constraints_to_candidates[other_col].add(rcd)
    @classmethod
    def solve_exact_cover(cls, constraints_to_candidates, candidates_to_constraints, partial=None):
        if partial is None:
            partial = []

        # Solved: all constraints are covered
        if not constraints_to_candidates:
            yield list(partial)
            return

        # Choose the most constrained column (fewest remaining candidates)
        col = min(constraints_to_candidates, key=lambda c: len(constraints_to_candidates[c]))
        if len(constraints_to_candidates[col]) == 0:
            return  # dead end

        # Try each candidate row that satisfies that column
        for rcd in list(constraints_to_candidates[col]):
            removed = cls.select(constraints_to_candidates, candidates_to_constraints, rcd)
            partial.append(rcd)

            yield from cls.solve_exact_cover(constraints_to_candidates, candidates_to_constraints, partial)

            partial.pop()
            cls.deselect(constraints_to_candidates, candidates_to_constraints, removed)

    
    def rows_to_grid(self, rows, N=9):
        #out = [[None for _ in range(N)] for _ in range(N)]
        for r, c, d in rows:
            self.sudoku_board[r][c] = d
        return self.sudoku_board

    def algorithm_x(self):
        constraints_to_candidates, candidates_to_constraints = type(self).build_cover_maps()
        partial = []

        # Pre-select (cover) all fixed clues
        for r in range(9):
            for c in range(9):
                v = self.sudoku_board[r][c]
                if isinstance(v, int):
                    if not (1 <= v <= 9):
                        return None

                    rcd = (r, c, v)

                    # Candidate must exist
                    if rcd not in candidates_to_constraints:
                        return None

                    # Contradiction checks: required columns must still exist and still allow rcd
                    for col in candidates_to_constraints[rcd]:
                        if col not in constraints_to_candidates:
                            return None
                        if rcd not in constraints_to_candidates[col]:
                            return None

                    type(self).select(constraints_to_candidates, candidates_to_constraints, rcd)
                    partial.append(rcd)

        # Find one solution
        sol_rows = next(type(self).solve_exact_cover(constraints_to_candidates, candidates_to_constraints, partial), None)
        if sol_rows is None:
            return None

        return self.rows_to_grid(sol_rows)



    def solve_sudoku_cp(self, possible_digits: dict[tuple[int, int], list[int]]) -> list[list[int]]:
        """
        Solve sudoku with constraint programming, treat confident digits + sudoku rules as hard constrants while uncertain cells
        are treated as soft constraints. Uncertain cells are given a list of candidate digits.
        Each uncertain cell gets assigned a penalty value, which is the rank of the chosen digit in the candidates list.
        (i.e. the lower the index of a chosen candidate digit from the candidates list, the smaller the associated penalty)
        The goal is to minimize the total sum of these penalties while enforcing the hard sudoku constraints.
        """

        model = cp_model.CpModel()

        X = [[model.NewIntVar(1, 9, f"x_{r}_{c}") for c in range(9)] for r in range(9)]

        # Sudoku contraints
        # Each row contains unique digits 1-9
        for r in range(9):
            model.AddAllDifferent(X[r])

        # Each column contains unique digits 1-9
        for c in range(9):
            model.AddAllDifferent([X[r][c] for r in range(9)])

        # Each block contains unique digits 1-9
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                model.AddAllDifferent([X[r][c] for r in range(br, br+3) for c in range(bc, bc+3)])

        penalties = []
        for r in range(9):
            for c in range(9):
                v = self.sudoku_board[r][c]
                if isinstance(v, int):
                    model.Add(X[r][c] == v)
                elif v == "Unsure": 

                    # Ranked list of candidates digits for that cell
                    cands = possible_digits[(r, c)]
                    p = model.NewIntVar(0, 8, f"p_{r}_{c}")

                    model.AddAllowedAssignments(
                        [X[r][c], p],
                        [[digit, rank] for rank, digit in enumerate(cands)])
                    penalties.append(p)

        # Choose solution that minimizes the penalty (change "Unsure" cells as little as possible such that penalty is kept small) 
        if penalties:
            model.Minimize(sum(penalties))

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        return [[solver.Value(X[r][c]) for c in range(9)] for r in range(9)]

