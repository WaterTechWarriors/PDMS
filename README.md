# PDF Ingestion and Processing Tool

A Python application for processing PDF files and creating structured outputs. This tool is designed for batch processing of PDF documents with a focus on annotation extraction and content structuring, featuring detailed logging and an interactive command-line interface.

## Demo Video

[![PDF Processing Tool Demo](https://img.youtube.com/vi/GGxD2veCMvE/0.jpg)](https://youtu.be/GGxD2veCMvE?si=kgZ6Jj-DVwOu6FaX)

Click the image above to watch a demonstration of how this tool works.

## Features

- 📄 Batch PDF processing
- 📑 Annotation extraction
- 📊 JSON output generation
- 📝 Markdown conversion for debugging
- 🔄 Progress tracking
- 📋 Detailed logging

## Installation

1. Clone this repository: 
```bash
git clone https://github.com/tirandagan/AdvancedRAGingest.git
cd AdvancedRAGingest
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies using Poetry:
```bash
poetry install
```

4. Activate the Poetry shell:
```bash
poetry shell
```

## Directory Structure

The application uses the following directory structure:

```
project_root/
├── input/              # Place your PDF files here
├── output/
│   ├── json/          # Generated JSON files with PDF content
│   └── annotations/   # Extracted annotations
├── logs/              # Application logs
├── pyproject.toml     # Poetry dependency management
└── config.yaml        # Configuration file
```

## Usage

1. Place your PDF files in the `input/` directory.

2. Ensure you're in the Poetry shell:
```bash
poetry shell
```

3. Run the application:
```bash
python 01_LoadPDFs.py
```

4. Select from two available tasks:
   - Option 1: "Ingest PDFs and create JSON & Annotations"
     - Processes PDF files from the input directory
     - Extracts content and annotations
     - Generates JSON output files
   - Option 2: "Create Debugging Markdowns from partition JSONs"
     - Creates markdown files from previously processed JSON files
     - Useful for debugging and content verification

## Output Description

The processing generates several types of output files:

### JSON Output (`output/json/`)
- Structured content extracted from PDFs
- Includes document metadata and text content
- Organized in a format suitable for further processing

### Annotations (`output/annotations/`)
- Contains extracted PDF annotations
- Includes highlights, comments, and other markup
- Preserved in structured format for analysis

## Logging

The application generates detailed logs in `pdf_converter.log`:
- Processing status and progress
- Warning and error messages
- Operation timestamps

The following log sources are managed:
- http.client (ERROR level)
- httpx (ERROR level)
- unstructured (ERROR level)
- unstructured_ingest (ERROR level)

## Configuration

The application uses a configuration system that can be customized through `config.yaml`. Configuration is loaded at startup and includes:
- Directory paths
- Processing options
- Logging settings

## Error Handling

The application includes error handling for:
- Invalid directory paths
- PDF processing errors
- Configuration issues
- File system operations

## Development

For development work:
```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
```

## License

(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.

## Support

For issues, questions, or suggestions, please [open an issue](https://github.com/tirandagan/AdvancedRAGingest/issues) on GitHub.
