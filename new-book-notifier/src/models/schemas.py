from typing import List, Optional
from pydantic import BaseModel

class WebhookResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None

class BookDetails(BaseModel):
    book_code: str
    title: str
    author: Optional[str] = None
    pdf_filename: Optional[str] = None
    file_size_mb: Optional[float] = None
    processing_method: str
    summary: str
    download_url: Optional[str] = None

class NewBookNotification(BaseModel):
    books: List[BookDetails]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
