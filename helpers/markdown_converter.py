"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

Markdown Conversion Module

This module provides functionality to convert JSON data from processed PDFs
into markdown format, preserving structure and content types.
"""

import os
import json
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .config import global_config
from .display import select_json_file

PAGE_FOOTER = "\n\n---\nPage {current_page}\n\n---\n\n"
console = Console()

def json_to_markdown(json_data, visual=False):
    """
    Converts JSON data to Markdown format.

    Args:
        json_data (list): A list of dictionaries containing structured content.

    Returns:
        str: The formatted Markdown content.
    """
    markdown_content = "\n"
    current_page = None
    page_content = ""
    
    for item in json_data:
        # Get the page number from metadata
        page_number = item['metadata'].get('page_number')
        
        # If we've moved to a new page, add the previous page's content with page number
        if page_number != current_page and current_page is not None:
            markdown_content += page_content
            markdown_content += PAGE_FOOTER.format(current_page=current_page)
            page_content = ""
        
        current_page = page_number
        category = item.get('type', 'Unknown')
        content = item.get('text', '')
        
        if category == 'Title':
            page_content += f"# {content}\n\n"
        elif category == 'NarrativeText':
            page_content += f"{content}\n\n"
        elif category == 'ListItem':
            page_content += f"- {content}\n"
        elif category == 'Table':
            page_content += item['metadata'].get('text_as_html', '') + "\n\n"           
        elif category == 'Image':
            image_base64 = item['metadata'].get('image_base64')
            if image_base64:
                if visual:
                    # Determine the image format (assuming it's either PNG or JPEG)
                    image_format = 'png' if image_base64.startswith('/9j/') else 'jpeg'
                    summary = f"<p style=\"line-height:.9; bgcolor: #000\"><span style=\"font-family:Tahoma; font-size:.7em; color: #705\">{item.get('llm_summary', 'No summary available')}</span></p>"
                    image_tag = f"![IMAGE:](data:image/{image_format};base64,{image_base64})"
                    page_content += f"| {image_tag}  |\n|:--:|\n| {summary} |\n\n"
                else:
                    page_content += f"Image: {summary}\n\n"
            else:
                page_content += f"> Image: {content or '?Unknown'}\n\n"
        else:
            page_content += f"{content}\n\n"
    
    # Add the last page's content
    if page_content:
        markdown_content += page_content
        markdown_content += PAGE_FOOTER.format(current_page=current_page)
    
    return markdown_content

def create_markdowns():
    """
    Creates markdown files from JSON data in the output directory.
    Allows user to select which JSON files to convert.
    """
    output_dir = os.path.realpath(global_config.get('DIRECTORIES', 'output_dir'))
    unstructured_json_dir = os.path.join(output_dir, '01_partitioned')
    json_files = select_json_file(unstructured_json_dir)
    
    if not json_files:
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Converting files to markdown", total=len(json_files))
        
        for json_file in json_files:
            try:
                progress.update(task, description=f"Converting {os.path.basename(json_file)}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                markdown_content = json_to_markdown(json_data)
                markdown_file = os.path.basename(os.path.splitext(json_file)[0] + '.md')
                markdown_file_path = os.path.join(output_dir, '03_markdown', markdown_file)
                with open(markdown_file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                progress.advance(task)
                logging.info(f"Created markdown file: {markdown_file}")
                console.print(f"Created: {os.path.basename(markdown_file)}", style="green")
                
            except Exception as e:
                console.print(f"Error converting {os.path.basename(json_file)}: {str(e)}", style="red")
                logging.error(f"Error converting {json_file}: {str(e)}")
