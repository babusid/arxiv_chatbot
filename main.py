"""
Main module for pdf -> markdown conversion API
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import md_parser

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
    "*",
    # Add other origins as needed
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/convert")
def init_conversion(pdf_path: str, bg: BackgroundTasks):
    """
    Starts the conversion process for the given PDF file,
    returns a job ID. Conversion should start in the background via a worker.
    """
    return md_parser.add_parse_job(pdf_path, bg)


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """
    Returns the status of the conversion job.
    """
    return md_parser.get_parse_job_status(job_id)


@app.get("/result/{job_id}")
def get_result(job_id: str):
    """
    Returns the result of the conversion job.
    """
    return md_parser.get_parse_job_result(job_id)
