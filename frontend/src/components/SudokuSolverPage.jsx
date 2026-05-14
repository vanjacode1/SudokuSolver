import { useState } from "react";
import axios from "axios";
import "../styles/SudokuSolverPage.css";

export default function SudokuSolverPage() {
  // store image user uploaded
  const [uploadedImage, setUploadedImage] = useState(null);

  // store solved image that the backend returns
  const [solvedImage, setSolvedImage] = useState(null);

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL;

  const resetState = () => {
    setSolvedImage(null);
    setStatus(null);
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    resetState();

    // show uploaded image in the browser
    const localImageUrl = URL.createObjectURL(file);
    setUploadedImage(localImageUrl);

    // send formdata to send the file to backend
    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      // send image to backend
      const response = await axios.post(
        `${API_URL}/api/sudoku-solver`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const data = response.data;

      // save backend status ("ok", "no_grid", "n_solution")
      setStatus(data.status);

      if (data.overlay_image) {
        setSolvedImage(`data:image/png;base64,${data.overlay_image}`);
      }
    } catch (error) {
      console.error(error);
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
        <h1 className="title">Sudoku Solver</h1>

        <p className="subtitle">
          Upload an image of a sudoku puzzle to solve it
        </p>

        <div className="uploadBox">
          <input
            type="file"
            accept="image/png, image/jpeg, image/jpg"
            onChange={handleImageUpload}
          />
        </div>

        {loading && <div className="message">Solving sudoku...</div>}

        {status === "no_grid" && (
          <div className="error">No sudoku puzzle detected</div>
        )}

        {status === "no_solution" && (
          <div className="error">No solution found</div>
        )}

        {status === "error" && (
          <div className="error">Something went wrong</div>
        )}

        <div className="content">
          {uploadedImage && (
            <div className="imageCard">
              <h3>Uploaded image</h3>
              <img src={uploadedImage} alt="Uploaded sudoku" />
            </div>
          )}

          {solvedImage && (
            <div className="imageCard">
              <h3>Solved Sudoku</h3>
              <img src={solvedImage} alt="Solved sudoku" />
            </div>
          )}
        </div>
      </div>
  );
}