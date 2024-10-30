# PDF Ingestion and Processing Tool

A powerful Python application for processing PDF files, extracting annotations, and generating structured output. This tool is designed to handle batch processing of PDF documents while maintaining detailed logging and providing user-friendly command-line interactions.

## Features

- 📄 Batch PDF processing
- 📑 Annotation extraction
- 🖼️ Bounding box image generation (optional)
- 📊 JSON output generation
- 📝 Markdown conversion capabilities
- 🔄 Progress tracking
- 📋 Detailed logging

## Installation

1. Clone this repository: 
```bash
git clone https://github.com/tirandagan/AdvancedRAGingest.git
cd AdvancedRAGingest
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Directory Structure

Before running the application, ensure you have the following directory structure:

project_root/
├── input/ # Place your PDF files here
├── output/
│ ├── json/ # Generated JSON files
│ ├── annotations/ # Extracted annotations
│ ├── images/ # Generated bounding box images
│ └── markdown/ # Generated markdown files
├── logs/ # Application logs
└── config.yaml # Configuration file

## Usage

1. Place your PDF files in the `input/` directory.

2. Run the application:

```
python 01_LoadPDFs.py
```


3. Select your desired task from the menu:
   - Option 1: Ingest PDFs and create JSON & Annotations
   - Option 2: Create Debugging Markdowns from partition JSONs

## Output Description

After processing, you'll find the following in your output directories:

### JSON Output (`output/json/`)
- Contains structured JSON files for each processed PDF
- Includes metadata, content, and annotation information
- Format: `{original_filename}_processed.json`

### Annotations (`output/annotations/`)
- Extracted annotations from the PDFs
- Includes highlights, comments, and other markup
- Format: `{original_filename}_annotations.json`

### Images (`output/images/`)
- Generated images showing bounding boxes of annotations
- Useful for debugging and verification
- Format: `{original_filename}_page_{number}.png`

### Markdown (`output/markdown/`)
- Generated markdown files for easy viewing
- Contains processed content in a readable format
- Format: `{original_filename}.md`

## Logging

The application maintains detailed logs in `pdf_converter.log`, including:
- Processing status
- Error messages
- Warning notifications
- Operation timestamps

## Configuration

You can modify the `config.yaml` file to customize:
- Input/output directory paths
- Processing options
- Logging levels
- Image generation settings

## Error Handling

The application includes robust error handling for:
- Invalid PDF files
- Missing directories
- Processing failures
- Permission issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.

## Support

For issues, questions, or suggestions, please [open an issue](your-repository-url/issues) on GitHub.
