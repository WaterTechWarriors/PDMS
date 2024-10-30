"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

PDF Ingestion and Processing Application

This script provides a command-line interface for processing PDF files.
It allows users to process PDF files from an input directory, extract 
annotations and optionally save bounding box images.

Key features:
- Configurable input and output directories
- Progress tracking for PDF processing
- Error handling and logging

Usage:
python 01_RAG_ingest_app.py
"""

import os

from helpers import *
from helpers.pdf_ingest import PDFProcessor
from helpers.logging import setup_logging
from helpers.generate_markdown import create_debugging_markdown

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

def is_valid_directory(path):
    return os.path.isdir(path)

def select_task():
    """Prompts user to select a task to perform."""
    tasks = [
        "Ingest PDFs and create JSON & Annotations",
        "Create Debugging Markdowns from partition JSONs",
        "Exit"
    ]
    
    console.print("\nAvailable tasks:", style="blue")
    for i, task in enumerate(tasks, 1):
        console.print(f"{i}. {task}")
    
    choice = Prompt.ask("\nSelect task", choices=[str(i) for i in range(1, len(tasks) + 1)])
    return tasks[int(choice) - 1]

def main():
    """Main function to run the PDF processing application."""
    console.print("PDF Processing Application", style="bold blue")
    console.print("-" * 50)
    
    setup_logging()
    load_config()
      
    while True:
        task = select_task()
        
        if task == "Ingest PDFs and create JSON & Annotations":
            input_dir = global_config.directories.input_dir
            processor = PDFProcessor()
            pdf_files = get_files_with_extension(input_dir, '.pdf')
            processor.process_pdfs(input_dir, pdf_files)
            
        elif task == "Create Debugging Markdowns from partition JSONs":
            create_debugging_markdown()
        
        elif task == "Exit":
            break
        
    console.print("\nApplication completed.", style="green")

if __name__ == "__main__":
    main()
