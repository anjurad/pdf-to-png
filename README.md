# WM5G PDF to PNG Batch Converter

A robust, test-driven CLI tool to batch-convert PDF files to PNG images, designed for reliability and maintainability. Built with Python 3.11, it leverages best practices for code quality, testing, and packaging.

## Features
- Converts all PDF files in a directory to PNG images (one image per page)
- Outputs images to a specified directory, preserving original filenames
- Clear logging and error handling
- 90%+ test coverage enforced via CI
- Option to overwrite existing PNG files

## Requirements
- Python 3.11 (recommended: use a virtual environment)
- [Poppler](https://poppler.freedesktop.org/) (for `pdf2image` backend)

## Installation
Clone the repository and install dependencies:
```sh
git clone <repo-url>
cd WM5G
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Or, for development:
# pip install -e .[dev]
```

**Install Poppler** (required for PDF conversion):
- **macOS**: `brew install poppler`
- **Ubuntu**: `sudo apt-get install poppler-utils`

## Usage
Convert all PDFs in the `data/` directory to PNGs in the `output/` directory:
```sh
python src/main.py --input-dir ./data --output-dir ./output [options]
```
Arguments:
- `--input-dir`: Directory containing PDF files (default: `./data`)
- `--output-dir`: Directory to save PNG images (default: `./output`)
- `--log-level`: Set logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; default: `INFO`)
- `--log-to-console`: Enable logging to console in addition to file
- `--overwrite`: Overwrite existing PNG files

### Example
```sh
python src/main.py --input-dir ./pdfs --output-dir ./images --log-level DEBUG --log-to-console --overwrite
```

## Logging

- All logs are written to `app.log` in the output directory specified by `--output-dir`.
- You can control the verbosity of logs using the `--log-level` option.
- To also see logs in your terminal, use the `--log-to-console` flag.
- Example:  
  ```bash
  python src/main.py --log-level DEBUG --log-to-console
  ```
- Log rotation is not enabled by default; the log file is appended to on each run.

## Project Structure
```
src/         # Source code
tests/       # Pytest unit tests (≥90% coverage, no live cloud calls)
data/        # Input PDFs (not versioned)
output/      # Output PNGs (not versioned)
pyproject.toml, requirements.txt, pytest.ini, uv.lock  # Dependency & test config
```

## Testing
Run all tests and check coverage:
```sh
pytest
# or, with coverage report:
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```
Tests use stubs/mocks for all I/O and cloud calls.

## Development Standards
- **Formatting**: [Ruff](https://docs.astral.sh/ruff/) (`ruff format`) for code style, linting, and import sorting.
- **Type Checking**: All code is type-annotated and includes a `py.typed` marker.
- **Documentation**: Google-style docstrings for all public modules, classes, and functions.
- **Dependencies**: Managed with [UV](https://github.com/astral-sh/uv) (`uv.lock`), fallback to pip-tools.
- **CI/CD**: Enforce ≥90% test coverage and linting in CI.

## Contributing
1. Fork and clone the repo.
2. Create a feature branch.
3. Add or update tests for your changes.
4. Run `ruff format .` and `ruff check .` before committing.
5. Open a pull request with a clear description.

## License
MIT License. See [LICENSE](LICENSE) for details.

---
*This project follows Azure Data & AI Python code-generation and testing best practices.*
