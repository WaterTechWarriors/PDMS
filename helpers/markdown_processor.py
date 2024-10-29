"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

Markdown Processing Module

This module provides functionality to process markdown files using
Unstructured.io API with chunking capabilities.
"""

import os
import json
import logging
import base64
import gzip
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .config import global_config, get_config
from unstructured.partition.md import partition_md
from unstructured.chunking.title import chunk_by_title
from unstructured.staging.base import elements_from_base64_gzipped_json

console = Console()


def process_markdown_files():
    """Process all markdown files in the output directory with chunking."""
    output_dir = os.path.realpath(global_config.get('DIRECTORIES', 'output_dir'))
    markdown_dir = os.path.join(output_dir, '03_markdown')
    chunked_dir = os.path.join(output_dir, '02_chunked')
    
    chunked_files = [f for f in os.listdir(chunked_dir) if f.endswith('.json')]
    
    if not chunked_files:
        console.print("No chunked files to process", style="yellow")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Processing chunked files", total=len(chunked_files))
        
        for chunked_file in chunked_files:
            try:
                progress.update(task, description=f"Processing {chunked_file}")
                
                # Full path to the markdown file
                chunked_file_path = os.path.join(chunked_dir, chunked_file)
                
                with open(chunked_file_path, 'r') as file:
                    chunks = json.load(file)

                
                # Convert chunks to JSON-serializable format
                chunks_data = []
                for chunk in chunks:
                    metadata = chunk["metadata"]
                    
                    # Get and decode original elements if they exist
                    orig_elements = None
                    if "orig_elements" in metadata:
                        orig_elements = elements_from_base64_gzipped_json(metadata["orig_elements"])
                        output_elements = []
                        for orig_element in orig_elements:
                            id = orig_element.id
                            type = orig_element.category
                            coordinates = orig_element.metadata.coordinates
                            image_description = orig_element.metadata.image_description if hasattr(orig_element.metadata,'image_description') else None
                            text = orig_element.text
                            output_elements.append({"id": id, "type": type, "coordinates": coordinates, "image_description": image_description, "text": text})
                    else:
                        output_elements = None
                    
                    chunk_dict = {
                        "text": chunk['text'],
                        "type": chunk['type'],
                        "orig_elements": output_elements,
                    }
                       
                    chunks_data.append(chunk_dict)
                
                # Save chunked output ----- NOT COMPLETE ----
                #######################################33
                base_name = os.path.splitext(chunked_file)[0]
                output_file_dir = os.path.join(output_dir, '05_output')
                os.makedirs(output_file_dir, exist_ok=True)
                output_file = os.path.join(output_file_dir, f"{base_name}_output.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(chunks_data, f, indent=2, ensure_ascii=False)
                
                progress.advance(task)
                logging.info(f"Processed {chunked_file} with chunking")
                console.print(f"Created: {os.path.basename(output_file)}", style="green")
                
            except Exception as e:
                console.print(f"Error processing {chunked_file}: {str(e)}", style="red")
                logging.error(f"Error processing {chunked_file}: {str(e)}")
