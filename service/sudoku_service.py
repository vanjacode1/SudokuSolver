import numpy as np
from image_processing.grid_extractor import ExtractSudokuFromImages
from image_processing.digit_extractor import ExtractDigitsFromSudoku
from image_processing.overlay import place_solution_on_image_warped
from model.inference import predict_digit_with_probs
from solver.sudoku_algorithms import SudokuSolver


def solve_sudoku_from_image(img: np.ndarray, model):

    sudoku_extractor = ExtractSudokuFromImages(img)
    warped = sudoku_extractor.warped_image

    if warped is None:
        return {"status": "no_grid", "warped": None, "overlay": None, "grid": None, "solution": None}
    
    sudoku_digits = ExtractDigitsFromSudoku(warped).digits

    sudoku = []
    sudoku_mask = [] 
    possible_digits = {}

    sudoku_row = []
    sudoku_row_mask = []
    for idx, digit_img in enumerate(sudoku_digits):
        row, col = divmod(idx, 9)

        cropped_cell = digit_img[2:26, 2:26]
        n_white_pix = np.sum(cropped_cell == 255)

        sudoku_row_mask.append(n_white_pix)


        if n_white_pix < 20:
            sudoku_row.append(None)
        else:
            pred_digit, confidence, probs = predict_digit_with_probs(digit_img, model)
            probs = probs.numpy()
            candidates = sorted(range(len(probs)), key = lambda i: probs[i], reverse=True)
            candidates = [i + 1 for i in candidates]
            #print(pred_digit, confidence, probs)


            if confidence < 0.85:
                sudoku_row.append("Unsure")
                possible_digits[(row, col)] = candidates
            else:
                sudoku_row.append(pred_digit)
        
        if len(sudoku_row) == 9:
            sudoku.append(sudoku_row)
            sudoku_row = []

            sudoku_mask.append(sudoku_row_mask)
            sudoku_row_mask = []

    if sum(cell is None for row in sudoku for cell in row) == 81:
        return {"status": "no_grid", "overlay": None}
    
    solution = SudokuSolver(sudoku).solve_sudoku_cp(possible_digits)
    if solution is None:
        return {"status": "no_solution", "overlay": None}
    
    sudoku_mask = np.array(sudoku_mask) >= 15

    overlay = place_solution_on_image_warped(warped, solution, sudoku_mask)
    return {"status": "ok", "overlay": overlay}