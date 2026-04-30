"""Resume parser tests."""

from io import BytesIO

from docx import Document

from backend.config import get_settings
from backend.core.analysis.resume_parser import ResumeParser


def test_pdf_text_extraction_succeeds(sample_resume_bytes):
    result = ResumeParser(get_settings()).parse_bytes("resume.pdf", sample_resume_bytes)
    assert "Python" in result["skills"]


def test_docx_text_extraction_succeeds():
    document = Document()
    document.add_paragraph("Python PyTorch Docker")
    buffer = BytesIO()
    document.save(buffer)
    result = ResumeParser(get_settings()).parse_bytes("resume.docx", buffer.getvalue())
    assert "PyTorch" in result["skills"]


def test_llm_extraction_returns_parsed_resume(sample_resume_bytes):
    result = ResumeParser(get_settings()).parse_bytes("resume.pdf", sample_resume_bytes)
    assert result["skills"]


def test_handles_empty_pdf():
    result = ResumeParser(get_settings()).extract_skills_from_text("")
    assert result == []


def test_file_size_validation():
    parser = ResumeParser(get_settings())
    oversized = b"a" * ((get_settings().MAX_RESUME_SIZE_MB * 1024 * 1024) + 1)
    try:
        parser.parse_bytes("resume.pdf", oversized)
    except ValueError as exc:
        assert "maximum size" in str(exc)


def test_skills_are_normalized_after_extraction():
    parser = ResumeParser(get_settings())
    assert parser.extract_skills_from_text("torch sklearn fastapi") == ["PyTorch", "scikit-learn", "FastAPI"]
