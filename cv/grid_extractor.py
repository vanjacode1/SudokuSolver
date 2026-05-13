import cv2
import numpy as np

RESIZE_WIDTH = 800
WARP_SIZE = 450

class ExtractSudokuFromImages:
    """
    Detect and persepctive transform a sudoku grid found in images.

    Steps:
    1. Use some standard image preprocessing steps (gaussian blur + adaptive thresholding)
    2. Contour detection
    3. Choose largest 4 corner contour as sudoku
    4. Order corners and apply perspective transform
    """
    def __init__(self, img_path):
        if isinstance(img_path, str):
            image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise ValueError(f"Could not read image from path: {img_path}")
        else:
            image = img_path
            if image is None:
                raise ValueError("Input image is None.")
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.image = image
        self.warped_image = None
        self.preprocess_pipeline()

    def _standardize_size(self):
        # Standardize the scale for each image such that the image preprocessing steps behave consistently across images
        width = RESIZE_WIDTH
        h, w = self.image.shape
        self.image = cv2.resize(self.image, (width, int(w * width/h)), interpolation = cv2.INTER_AREA)
    
    def _extract_sudoku_grid(self):
        # Reduce noise in the image before adaptove thresholding
        image_blur = cv2.GaussianBlur(self.image, (15, 15), 0)

        image_binary = cv2.adaptiveThreshold(image_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Find outer most contour, likely the sudoku border
        contours, _ = cv2.findContours(image_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        sudoku_corners = []
        for c in contours:
            area = cv2.contourArea(c)

            # Ignore small contours
            if area < 1000:
                continue
            peri = cv2.arcLength(c, True)
            corners = cv2.approxPolyDP(c, 0.08*peri, True)

                # If a contour has the largest area and 4 corners, then assume it's the sudoku
                # This check is too coarse but works for now
                # It would be better to check whether largest area has 4 corners AND 9 vertical and 9 horizontal lines in addition to 81 cells
            if len(corners) == 4:
                sudoku_corners = corners
                return sudoku_corners
        return None
    
    @staticmethod
    def _order_corners(contour_corners):
        coordinate_sum = contour_corners.sum(axis=1)
        coordinate_diff = contour_corners[:, 0] - contour_corners[:, 1] 

        # Top left has smallest sum
        tl = contour_corners[np.argmin(coordinate_sum)]

        # Bottom right has largest sum
        br = contour_corners[np.argmax(coordinate_sum)]

        # Top right has largest difference
        tr = contour_corners[np.argmax(coordinate_diff)]

        # Bottom left has smallest difference
        bl = contour_corners[np.argmin(coordinate_diff)]

        return np.array([tl, tr, bl, br], dtype=np.float32)
    
    def _image_warping(self, sudoku_corners):
        # Warp sudoku to a fixed square size (450x450)
        try:
            sudoku_corners = sudoku_corners.reshape((4,2))
        except:
            raise AttributeError("No sudoku found in the picture")

        # Coordinates of original image
        pts1 = self._order_corners(sudoku_corners)

        # Coordinates you want the warped image to have
        pts2 = np.float32([
            [0, 0],
            [450, 0],
            [0, 450],
            [450, 450]
        ])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgwarp = cv2.warpPerspective(self.image, matrix, (WARP_SIZE, WARP_SIZE))

        return imgwarp
    
    def preprocess_pipeline(self):
        self._standardize_size()
        sudoku_corners = self._extract_sudoku_grid()
        if sudoku_corners is None or len(sudoku_corners) == 0:
            self.warped_image = None
        else:
            warped_image = self._image_warping(sudoku_corners)
            self.warped_image = warped_image


