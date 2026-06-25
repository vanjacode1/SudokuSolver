from ortools.sat.python import cp_model
from itertools import product


class SudokuSolver:
    """
    Solver for 9x9 Sudoku puzzles.

    Supports two approaches:
    1. Backtracking for standard recursive solving.
    2. OR-Tools CP-SAT for puzzles with uncertain cells and ranked candidate digits.
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

