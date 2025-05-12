"""
This module is responsible for handling the pdf-to-markdown conversion process.
"""

from uuid import uuid4
import enum
from urllib.request import urlretrieve
import tempfile
import os
import pymupdf4llm
from fastapi import BackgroundTasks


class JobStatus(enum.Enum):
    """
    Enum for job status
    """

    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"


# stores job status - eventually this should probably be a database table or something
parse_jobs: dict[str, dict] = {}


def add_parse_job(pdf_path: str, bg: BackgroundTasks) -> dict:
    """
    Creates and adds a new parse job to the queue, returns a job ID.
    """
    job_id = uuid4().hex
    parse_jobs[job_id] = {"status": JobStatus.QUEUED}
    bg.add_task(convert_pdf_to_markdown, job_id, pdf_path)
    return {"job_id": job_id}


def get_parse_job_status(job_id: str) -> dict:
    """
    Returns the status of the parse job
    """
    if job_id not in parse_jobs:
        return {"error": "Job ID not found"}
    return parse_jobs[job_id]["status"]


def get_parse_job_result(job_id: str) -> dict:
    """
    Returns the result of the parse job
    """
    if job_id not in parse_jobs:
        return {"error": "Job ID not found"}
    if parse_jobs[job_id]["status"] != JobStatus.COMPLETED:
        return {"error": "Job is not completed yet"}
    return parse_jobs[job_id]["markdown"]


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
    parse_jobs[job_id]["status"] = JobStatus.COMPLETED
    parse_jobs[job_id]["markdown"] = markdown
