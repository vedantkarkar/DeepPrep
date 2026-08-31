import pytest
from app.domains.candidate.text_extractor import (
    ResumeTextExtractor,
    UnsupportedFileTypeError,
    OversizedFileError,
    EmptyDocumentError,
    CorruptDocumentError,
)

def test_extract_pdf_valid():
    with open("data/resumes/demo_resume.pdf", "rb") as f:
        pdf_bytes = f.read()
    text = ResumeTextExtractor.extract_from_bytes(pdf_bytes, "demo_resume.pdf")
    assert "AARAV DESHMUKH" in text
    assert "EDUCATION" in text
    assert len(text) > 200

def test_extract_docx_valid():
    with open("data/resumes/demo_resume.docx", "rb") as f:
        docx_bytes = f.read()
    text = ResumeTextExtractor.extract_from_bytes(docx_bytes, "demo_resume.docx")
    assert "AARAV DESHMUKH" in text
    assert "TECHNICAL SKILLS" in text
    assert len(text) > 200

def test_extract_txt_valid():
    with open("data/resumes/demo_resume.txt", "rb") as f:
        txt_bytes = f.read()
    text = ResumeTextExtractor.extract_from_bytes(txt_bytes, "demo_resume.txt")
    assert "AARAV DESHMUKH" in text

def test_reject_unsupported_file_type():
    with pytest.raises(UnsupportedFileTypeError):
        ResumeTextExtractor.extract_from_bytes(b"dummy binary", "malicious.exe")

    with pytest.raises(UnsupportedFileTypeError):
        ResumeTextExtractor.extract_from_bytes(b"dummy binary", "photo.png")

def test_reject_oversized_file():
    huge_bytes = b"0" * (6 * 1024 * 1024) # 6 MB
    with pytest.raises(OversizedFileError):
        ResumeTextExtractor.extract_from_bytes(huge_bytes, "huge.pdf")

def test_reject_empty_file():
    with pytest.raises(EmptyDocumentError):
        ResumeTextExtractor.extract_from_bytes(b"", "empty.pdf")

def test_reject_corrupt_pdf():
    with pytest.raises(CorruptDocumentError):
        ResumeTextExtractor.extract_from_bytes(b"Not a real PDF", "corrupt.pdf")

def test_reject_corrupt_docx():
    with pytest.raises(CorruptDocumentError):
        ResumeTextExtractor.extract_from_bytes(b"Not a real DOCX", "corrupt.docx")
