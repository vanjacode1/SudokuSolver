from fastapi import UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
from model.inference import load_digitnet
from service.sudoku_service import solve_sudoku_from_image
import numpy as np
import cv2
import base64

router = APIRouter()

model = load_digitnet("weights/sudoku_digit_cnn_best.pth")

def image_to_base64(img: np.ndarray) -> str:

    success, buffer = cv2.imencode(".jpg", img)

    if not success:
        raise ValueError("Could not encode image")

    return base64.b64encode(buffer).decode("utf-8")


@router.post("")
async def solve_sudoku(file: UploadFile = File(...)):
    image_bytes = await file.read()

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    print(img)

    if img is None:
        return JSONResponse(
            status_code=400,
            content={"status": "invalid_image", "message": "Could not read image"},
        )

    result = solve_sudoku_from_image(img, model)

    response = {
        "status": result["status"],
        "overlay_image": None,
    }

    if result["overlay"] is not None:
        response["overlay_image"] = image_to_base64(result["overlay"])

    return response