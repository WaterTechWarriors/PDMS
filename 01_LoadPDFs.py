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

import logging
import os
import json
from helpers import *
from helpers.llm_summaries import build_json_image_summaries
from helpers.pdf_ingest import ingest_pdfs
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def setup_logging():
    """Sets up logging for the application."""
    logging.basicConfig(
        filename='pdf_converter.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )

def process_pdfs(pdf_files):
    """
    Processes PDF files for annotation extraction and image saving.
    
    Args:
        pdf_files: List of PDF filenames to process.
    """
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    save_bbox_images = global_config.get('PDF_PROCESSING', 'save_bbox_images')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter PDFs that already have JSON output
    pdfs_to_process = []
    for pdf_file in pdf_files:
        json_file = os.path.join(output_dir, pdf_file + '.json')
        if os.path.exists(json_file):
            if Confirm.ask(f"JSON output for {pdf_file} already exists. Overwrite?"):
                pdfs_to_process.append(pdf_file)
        else:
            pdfs_to_process.append(pdf_file)
    
    if not pdfs_to_process:
        console.print("No PDFs to process", style="yellow")
        return
        
    # Ingest PDFs
    console.print("\nIngesting PDFs...", style="blue")
    ingest_pdfs(input_dir, pdfs_to_process)
    
    # Process each PDF for bounding boxes if enabled
    if save_bbox_images:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            for pdf_file in pdfs_to_process:
                try:
                    file_path = os.path.join(input_dir, pdf_file)
                    num_pages = get_pdf_page_count(file_path)
                    
                    task = progress.add_task(f"Processing {pdf_file}", total=num_pages)
                    process_pdf_pages(pdf_file, num_pages, progress)
                    
                    logging.info(f"Processed {pdf_file}")
                except Exception as e:
                    logging.error(f"Error processing {pdf_file}: {str(e)}")
                    console.print(f"Error processing {pdf_file}: {str(e)}", style="red")

def select_task():
    """Prompts user to select a task to perform."""
    tasks = [
        "Ingest PDFs and create JSON & Annotations",
        "Create Markdowns from JSON output files",
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
    
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    
    while True:
        task = select_task()
        
        if task == "Ingest PDFs and create JSON & Annotations":
            if not is_valid_directory(input_dir) or not is_valid_directory(output_dir):
                console.print("Error: Invalid input or output directory!", style="red")
                continue
                
            pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
            if not pdf_files:
                console.print("No PDF files found in the input directory!", style="yellow")
                continue
                
            process_pdfs(pdf_files)
            
        elif task == "Create Markdowns from JSON output files":
            process_markdown_files()
        
        if not Confirm.ask("\nWould you like to perform another task?"):
            break
    
    console.print("\nApplication completed.", style="green")

if __name__ == "__main__":
    main()
