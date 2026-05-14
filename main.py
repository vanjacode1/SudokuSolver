from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import sudoku

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://sudoku-solver-ebns.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sudoku.router, prefix = "/api/sudoku-solver")
    
