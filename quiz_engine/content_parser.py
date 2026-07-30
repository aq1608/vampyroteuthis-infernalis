"""
Content Parser - Extract text from PDFs and raw text input.

Handles:
- PDF file uploads (via pdfplumber)
- Raw text/pasted content
- Text chunking for processing
"""

from __future__ import annotations

import pdfplumber


def parse_pdf(uploaded_file) -> str:
    """
    Extract text content from an uploaded PDF file.

    Args:
        uploaded_file: A Streamlit UploadedFile object (PDF).

    Returns:
        Extracted text as a single string.
    """
    text_pages = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    return "\n\n".join(text_pages)


def parse_text(raw_text: str) -> str:
    """
    Clean and normalize raw text input.

    Args:
        raw_text: Raw text pasted by the user.

    Returns:
        Cleaned text string.
    """
    # Strip extra whitespace and normalize line breaks
    lines = raw_text.strip().splitlines()
    cleaned = "\n".join(line.strip() for line in lines if line.strip())
    return cleaned


def chunk_text(text: str, max_chunk_size: int = 3000) -> list[str]:
    """
    Split text into manageable chunks for API processing.

    Splits on paragraph boundaries to preserve context.

    Args:
        text: Full text content.
        max_chunk_size: Maximum characters per chunk.

    Returns:
        List of text chunks.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
