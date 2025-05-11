"""
Main module for pdf -> markdown conversion API
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import enum
from uuid import uuid4
import pymupdf4llm
import tempfile, os
from urllib.request import urlretrieve

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


class JobStatus(enum.Enum):
    """
    Enum for job status
    """

    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"


# stores job status - eventually this should be a database table
job_status_dict: dict[str, dict] = {}


def convert_pdf_to_markdown(job_id: str, pdf_path: str) -> str:
    """
    Converts a PDF file to markdown using pymupdf4llm
    """
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        urlretrieve(pdf_path, path)
        markdown = pymupdf4llm.to_markdown(path, embed_images=True)
    finally:
        # 4. No footprint left behind
        os.remove(path)
    job_status_dict[job_id]["status"] = JobStatus.COMPLETED
    job_status_dict[job_id]["markdown"] = markdown


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/convert")
def init_conversion(pdf_path: str, bg: BackgroundTasks):
    """
    Starts the conversion process for the given PDF file,
    returns a job ID. Conversion should start in the background via a worker.
    """
    print(pdf_path)
    print(job_status_dict)

    job_id = uuid4().hex
    job_status_dict[job_id] = {"status": JobStatus.QUEUED}
    bg.add_task(convert_pdf_to_markdown, job_id, pdf_path)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """
    Returns the status of the conversion job.
    """
    if job_id not in job_status_dict:
        return {"error": "Job ID not found"}
    return job_status_dict[job_id]["status"]


@app.get("/result/{job_id}")
def get_result(job_id: str):
    """
    Returns the result of the conversion job.
    """
    if job_id not in job_status_dict:
        return {"error": "Job ID not found"}
    if job_status_dict[job_id]["status"] != JobStatus.COMPLETED:
        return {"error": "Job is not completed yet"}
    return job_status_dict[job_id]["markdown"]
