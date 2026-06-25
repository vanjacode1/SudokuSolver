# Sudoku Solver

**Solve real Sudoku puzzles from images**

Sudoku Vision Solver is an image-based puzzle-solving application that allows users to upload a photo of a Sudoku puzzle. The app detects the Sudoku grid, extracts the existing numbers, solves the puzzle, and overlays the completed solution onto a perspective warped image of the original photo.

## Live Demo
[Try the app here](https://sudoku-solver-frontend-wui7.onrender.com/)

## About This Project

Instead of manually entering a puzzle, users can simply upload a photo and see the solved result directly.

1. The user uploads or captures a picture of a Sudoku puzzle.
2. The app detects the Sudoku grid in the image.
3. The existing digits are extracted from the puzzle.
4. The Sudoku is solved algorithmically.
5. The missing numbers are drawn back onto a perspective warped image.

## Accepted Photos

To get the most accurate result, please upload a clear photo of a Sudoku puzzle.

- Full Sudoku grid is visible
- Puzzle is printed clearly
- Image is sharp and not blurry
- Good lighting
- Minimal shadows

<p align="center">
  <img src="sudoku_photos/sudoku_8.jpg" alt="Accepted Sudoku Example 1" width="220">
  <img src="sudoku_photos/sudoku_38.jpg" alt="Accepted Sudoku Example 2" width="220">
  <img src="sudoku_photos/sudoku_176.jpg" alt="Accepted Sudoku Example 3" width="220">
</p>