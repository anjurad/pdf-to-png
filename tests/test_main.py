"""Unit tests for PDF to PNG batch converter CLI."""

import sys
from pathlib import Path
from unittest import mock

import pytest

import src.main as main_mod

PDF_SYNTAX_ERROR = getattr(main_mod, "PDFSyntaxError", None)
PDF_CONVERSION_ERROR = getattr(main_mod, "PdfConversionError", RuntimeError)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a dummy PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF\n")  # Minimal PDF header/footer
    return pdf_path


def test_parse_args_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test parse_args uses default directories when not specified."""
    test_args = ["main.py"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = main_mod.parse_args()
    assert args.input_dir.name == "data"
    assert args.output_dir.name == "output"


def test_pdf_to_pngs_success(tmp_path: Path, sample_pdf: Path) -> None:
    """Test successful PDF to PNG conversion."""
    # Mock convert_from_path to return a list of mock images
    with mock.patch("src.main.convert_from_path") as mock_convert:
        mock_img = mock.Mock()
        mock_convert.return_value = [mock_img, mock_img]
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        result = main_mod.pdf_to_pngs(sample_pdf, output_dir)
        assert len(result) == 2
        for path in result:
            assert path.parent == output_dir
        assert mock_img.save.call_count == 2


def test_pdf_to_pngs_failure(tmp_path: Path, sample_pdf: Path) -> None:
    """Test PDF to PNG conversion raises on error."""
    if PDF_SYNTAX_ERROR is not None:
        with mock.patch("src.main.convert_from_path", side_effect=PDF_SYNTAX_ERROR("bad pdf")):
            with pytest.raises(PDF_CONVERSION_ERROR):
                main_mod.pdf_to_pngs(sample_pdf, tmp_path)
    else:
        # Fallback for environments where PDFSyntaxError is not available
        with mock.patch("src.main.convert_from_path", side_effect=Exception("bad pdf")):
            with pytest.raises(PDF_CONVERSION_ERROR):
                main_mod.pdf_to_pngs(sample_pdf, tmp_path)


def test_main_no_pdfs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main exits gracefully if no PDFs are found."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    monkeypatch.setattr(sys, "argv", ["main.py", "--input-dir", str(input_dir), "--output-dir", str(output_dir)])
    # main() now returns exit code instead of calling sys.exit
    assert main_mod.main() == 0


def test_main_invalid_input_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main exits with error if input directory does not exist."""
    input_dir = tmp_path / "doesnotexist"
    output_dir = tmp_path / "output"
    monkeypatch.setattr(sys, "argv", ["main.py", "--input-dir", str(input_dir), "--output-dir", str(output_dir)])
    assert main_mod.main() == 1
