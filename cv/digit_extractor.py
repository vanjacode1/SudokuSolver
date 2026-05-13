import cv2
import numpy as np


class ExtractDigitsFromSudoku:
    """
    Detect and extract sudoku cells from a warped sudoku image (450x450).
    Each sudoku cell is resized to a 28x28 image

    Steps:
    1. Use some standard image preprocessing steps (gaussian blur + adaptive thresholding)
    2. Remove the grid lines such that only digits remain in place
    3. Remove small components/noise
    3. Slice into sudoku cells and resize to 28x28 images
    """
    def __init__(self, img_path):
        self.img_path = img_path
        self.digits = []
        self._extract_digits()

    @staticmethod
    def _remove_grid_lines(binary_image):

        # Horizontal lines
        horiz_size = 30
        horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horiz_size, 1))
        horiz_lines = cv2.erode(binary_image, horiz_kernel, iterations=1)

        # Vertical lines
        vert_size = 30
        vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vert_size))
        vert_lines = cv2.erode(binary_image, vert_kernel, iterations=1)

        # Remove horizontal lines from image
        no_horiz_lines = cv2.subtract(binary_image, horiz_lines)

        # Remove vertical lines from image
        digit_only_grid = cv2.subtract(no_horiz_lines, vert_lines)

        return digit_only_grid
    
    @staticmethod
    def _remove_noise(binary_image):
        kernel = np.ones((2, 2), np.uint8)

        # Remove small white specks 
        digit_only_grid = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel, iterations=1)

        # Thicken digits 
        digit_only_grid = cv2.morphologyEx(digit_only_grid, cv2.MORPH_CLOSE, kernel, iterations=1)


        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(digit_only_grid, connectivity=4)

        # Filter connected components to further remove noise in the image
        min_area = 80 
        digit_only_grid = np.zeros_like(digit_only_grid)
        for i in range(1, num_labels):
            # Get pixel area of component
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                digit_only_grid[labels == i] = 255

        return digit_only_grid

    def _clean_up_image(self):

        # Convert to a clean binary sudoku image 
        image_blur = cv2.GaussianBlur(self.image, (7, 7), 0)
        binary_image = cv2.adaptiveThreshold(image_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        digit_only_grid = self._remove_grid_lines(binary_image)
        digit_only_grid = self._remove_noise(digit_only_grid)
        return digit_only_grid
    
    def _extract_digits(self):
        self.image = self.img_path 
        sudoku = self._clean_up_image()
        h, w = sudoku.shape
        cell_h = h // 9
        cell_w = w // 9
        for row in range(9):
            for col in range(9):
                cell = sudoku[cell_h*row : cell_h + cell_h*row, cell_w*col: cell_w + cell_w*col]
                digit_img = cv2.resize(cell, (28, 28), interpolation=cv2.INTER_AREA)
                self.digits.append(digit_img)