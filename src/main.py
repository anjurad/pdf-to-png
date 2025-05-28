"""PDF to PNG batch converter CLI.

Reads PDF files from an input directory, converts each page to PNG, and writes them to an output directory.

Usage:
    python main.py --input-dir ./data --output-dir ./output
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from pdf2image import convert_from_path  # type: ignore
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
from PIL import Image


class PdfConversionError(RuntimeError):
    """Raised when PDF to PNG conversion fails."""

    pass


def get_logger() -> logging.Logger:
    """Get a module-level logger."""
    return logging.getLogger(__name__)


def configure_logging(output_dir: Path, log_level: str = "INFO", log_to_console: bool = False) -> None:
    """Configure logging for the CLI.

    Args:
        output_dir (Path): Directory where the log file will be written.
        log_level (str): Logging level (e.g., 'INFO', 'DEBUG').
        log_to_console (bool): If True, also log to the console.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "app.log"
    handlers: list[logging.Handler] = [logging.FileHandler(log_file, mode="a", encoding="utf-8")]
    if log_to_console:
        handlers.append(logging.StreamHandler())
    root_logger = logging.getLogger()
    # Remove all handlers associated with the root logger object (avoid duplicate logs if reconfigured)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args (list[str] | None): List of CLI arguments or None for sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments with input_dir, output_dir, log_level, and log_to_console.
    """
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to PNG images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data",
        help="Directory containing PDF files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "output",
        help="Directory to save PNG images.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level.",
    )
    parser.add_argument(
        "--log-to-console",
        action="store_true",
        help="Enable logging to console in addition to file.",
    )
    return parser.parse_args(args)


def pdf_to_pngs(pdf_path: Path, output_dir: Path, overwrite: bool = False) -> list[Path]:
    """Convert a PDF file to PNG images, one per page.

    Args:
        pdf_path (Path): Path to the PDF file.
        output_dir (Path): Directory to save PNG images.
        overwrite (bool): Whether to overwrite existing PNGs.

    Returns:
        list[Path]: List of output PNG file paths.

    Raises:
        PdfConversionError: If PDF conversion fails.
    """
    logger = get_logger()
    try:
        images: list[Image.Image] = convert_from_path(str(pdf_path))
    except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as e:
        logger.error(f"Failed to convert {pdf_path}: {e}")
        raise PdfConversionError(f"PDF conversion failed for {pdf_path}") from e

    output_paths: list[Path] = []
    for i, img in enumerate(images, start=1):
        output_path = output_dir / f"{pdf_path.stem}_page_{i}.png"
        if output_path.exists() and not overwrite:
            logger.info(f"Skipping existing file: {output_path}")
            continue
        try:
            img.save(output_path, "PNG")
            output_paths.append(output_path)
            logger.info(f"Saved {output_path}")
        except OSError as e:
            logger.error(f"Failed to save {output_path}: {e}")
            raise PdfConversionError(f"Failed to save {output_path}") from e
    return output_paths


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args (list[str] | None): CLI arguments or None for sys.argv.

    Returns:
        int: Exit code (0 for success, 1 for error, 0 for no PDFs found).
    """
    parsed = parse_args(args)
    configure_logging(parsed.output_dir, parsed.log_level, parsed.log_to_console)
    logger = get_logger()
    input_dir: Path = parsed.input_dir
    output_dir: Path = parsed.output_dir

    if not input_dir.is_dir():
        logger.error(f"Input directory does not exist: {input_dir}")
        return 1
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Cannot create output directory {output_dir}: {e}")
        return 1
    if not os.access(str(output_dir), os.W_OK):
        logger.error(f"Output directory is not writable: {output_dir}")
        return 1

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return 0

    exit_code = 0
    for pdf_file in pdf_files:
        try:
            pdf_to_pngs(pdf_file, output_dir)
        except PdfConversionError as e:
            logger.error(e)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
