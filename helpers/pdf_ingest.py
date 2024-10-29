"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

PDF Ingestion Module

This module provides functions to ingest PDF files using the Unstructured.io API.
It processes PDFs to extract structured data and save it in a specified output directory.

Key features:
- Ingest PDFs and extract structured data
- Configure processing options via a configuration file
- Handle multiple PDF files in a directory

Usage:
- Use `ingest_pdfs()` to process and ingest PDF files.
- Use `get_pdf_files()` to retrieve PDF files from a directory.
"""

import logging
import os
import json
from .llm_summaries import enrich_json_with_summaries
from rich.console import Console
from .config import get_config

from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (LocalIndexerConfig,LocalDownloaderConfig,LocalConnectionConfig,LocalUploaderConfig)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig

console = Console()

def ingest_pdfs(input_dir, pdf_files):
    """
    Ingest PDF files using the Unstructured.io API.

    Args:
        input_dir (str): Directory containing PDF files.
        pdf_files (list): List of PDF filenames to process.
    """
    # Configure logging
    unstructured_logger = logging.getLogger('unstructured_ingest.v2')
    unstructured_logger.setLevel(logging.CRITICAL)
    
    show_progressbar = get_config('PDF_PROCESSING', 'SHOW_PROGRESSBAR', fallback='False').lower() == 'true'
    
    output_dir = os.path.realpath(get_config('DIRECTORIES', 'OUTPUT_DIR'))
    partitioned_dir = os.path.join(output_dir, '01_partitioned')
    chunked_dir = os.path.join(output_dir, '02_chunked')
    work_dir = os.path.join(output_dir, 'temp')
    
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(partitioned_dir, exist_ok=True)
    os.makedirs(chunked_dir, exist_ok=True)
    
    unstructured_api_key = get_config('API_KEYS', 'UNSTRUCTURED_API_KEY')
    unstructured_url = get_config('API_KEYS', "UNSTRUCTURED_URL")
    
    console.print(f"Processing {len(pdf_files)} PDF files...", style="blue")
    
    processor_config       = ProcessorConfig(num_processes=3,verbose=False,tqdm=True,work_dir=work_dir)
    partitioner_config     = PartitionerConfig(
            partition_by_api=True,
            strategy="hi_res",
            api_key=unstructured_api_key,
            partition_endpoint=unstructured_url,
            extract_image_block_to_payload=True,
            additional_partition_args={
                "coordinates": True,
                "extract_image_block_types": ["Image","Table"],
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15
            }
        )
    
    # First Pipeline: Partitioning
    console.print("Starting partitioning...", style="blue")
    Pipeline.from_configs(
        context=processor_config,
        indexer_config=LocalIndexerConfig(input_path=input_dir),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=partitioner_config,
        uploader_config=LocalUploaderConfig(output_dir=partitioned_dir)
    ).run()
    
    console.print("PDF partitioning completed. Enhancing image metadata...", style="green")
    
    # Enhance image metadata
    json_files = [os.path.join(partitioned_dir, f) for f in os.listdir(partitioned_dir) if f.endswith('.json')]
    for json_file in json_files:
        try:
            enrich_json_with_summaries(json_file)
        except Exception as e:
            console.print(f"Error processing {json_file}: {str(e)}", style="red")
            logging.error(f"Error processing {json_file}: {str(e)}")


    console.print("Starting chunking...", style="blue")
    
    # Second Pipeline: Chunking
    # Create fresh configurations for the chunking pipeline
    
    Pipeline.from_configs(
        context=ProcessorConfig(num_processes=3,verbose=False,tqdm=True,work_dir=work_dir),
        indexer_config=LocalIndexerConfig(input_path=partitioned_dir),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=partitioner_config,        
        chunker_config=ChunkerConfig(chunking_strategy="by_title",chunk_max_characters=1500,chunk_overlap=150),
        uploader_config=LocalUploaderConfig(output_dir=chunked_dir)
    ).run()
    
    console.print("Chunking completed", style="green")
    
    # Rename files to remove duplicate .json extension
    chunked_files = [f for f in os.listdir(chunked_dir) if f.endswith('.json.json')]
    for file in chunked_files:
        old_path = os.path.join(chunked_dir, file)
        new_path = os.path.join(chunked_dir, file.replace('.json.json', '.json'))
        os.rename(old_path, new_path)
    
    console.print(f"Renamed {len(chunked_files)} files to remove duplicate .json extension", style="green")


def get_pdf_files(directory):
    """
    Get all PDF files in the specified directory.

    Args:
        directory (str): The directory to search for PDF files.

    Returns:
        list: List of PDF filenames.
    """
    return [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    
def get_json_file_elements(pdf_filename):
    """
    Get the elements from the JSON file associated with a PDF.

    Args:
        pdf_filename (str): The PDF filename (without extension).

    Returns:
        list: The JSON data elements.
    """
    file_path = pdf_filename +'.json'
    with open(file_path, 'r') as file:
        return json.load(file)
