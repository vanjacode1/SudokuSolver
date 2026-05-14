import cv2
import numpy as np

def place_solution_on_image_warped(out: np.ndarray, solution: list[list[int]], mask: np.ndarray):
    h, w = out.shape
    cell_h = h // 9
    cell_w = w // 9
    for row in range(9):
        for col in range(9):
            cell_location = (cell_w * (col + 1) - 33, cell_h * (row + 1) - 15)            
            if not mask[row][col]:
                out = cv2.putText(out, str(solution[row][col]), cell_location, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return out
