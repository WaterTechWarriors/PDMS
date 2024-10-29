"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

PDF Annotation and Visualization Tool (Unstructured.io API version)

This module provides functionality to annotate and visualize PDF pages with bounding boxes
around different types of content using the Unstructured.io API.
"""

import fitz
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image
import os
import logging
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from .config import global_config
from .pdf_ingest import get_json_file_elements

console = Console()

def log_to_file():
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler('pdf_converter.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)


def plot_pdf_with_boxes(pdf_page, documents, output_filename, output_dir):
    """
    Annotate a PDF page with bounding boxes for different content types and save as an image.
    Skip if the output image already exists.
    """
    base_filename = os.path.splitext(os.path.basename(output_filename))[0]
    complete_image_path = os.path.join(
        output_dir, 
        f"{base_filename}-{pdf_page.number + 1}-annotated.jpg"
    )
    
    # Skip if file already exists
    if os.path.exists(complete_image_path):
        logging.info(f"Skipping existing file: {complete_image_path}")
        return
        
    pix = pdf_page.get_pixmap()
    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    fig, ax = plt.subplots(1, figsize=(20, 20))
    ax.imshow(pil_image)
    
    category_to_color = {
        "Title": "orchid",
        "Image": "forestgreen",
        "Table": "tomato",
        "ListItem": "gold",
        "NarrativeText": "deepskyblue",
    }
    
    boxes_drawn = 0
    for doc in documents:
        category = doc['type']
        c = doc['metadata']['coordinates']
        points = c['points']
        layout_width = c['layout_width']
        layout_height = c['layout_height']

        scaled_points = [
            (x * pix.width / layout_width, y * pix.height / layout_height)
            for x, y in points
        ]
        box_color = category_to_color.get(category, "deepskyblue")
        polygon = patches.Polygon(
            scaled_points, linewidth=2, edgecolor=box_color, facecolor="none"
        )
        ax.add_patch(polygon)
        boxes_drawn += 1
    
    legend_handles = [patches.Patch(color=color, label=category) 
                     for category, color in category_to_color.items()]
    ax.axis("off")
    ax.legend(handles=legend_handles, loc="upper right")
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(complete_image_path, format="jpg", dpi=300)
    plt.close(fig)

    logging.info(f"{boxes_drawn} annotations on page {pdf_page.number + 1} of: {base_filename}")

def get_pdf_page_count(file_path):
    """
    Get the number of pages in a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        int: The number of pages in the PDF.
    """
    with fitz.open(file_path) as pdf:
        return len(pdf)

def process_pdf_pages(file_name: str, num_pages: int, progress=None):
    """
    Process the pages of a PDF file, creating an annotated image for each page.

    Args:
        file_name (str): Name of the PDF file.
        num_pages (int): Total number of pages in the PDF.
        progress (Progress, optional): Progress instance for tracking. If None, no progress is shown.
    """
    output_dir = global_config.get('DIRECTORIES', 'output_dir')
    input_dir = global_config.get('DIRECTORIES', 'input_dir')
    
    image_dir = os.path.join(output_dir, '02_bounding_boxes')
    
    input_json_path = os.path.join(output_dir, '01_partitioned', file_name )
    input_file_path = os.path.join(input_dir, file_name)
    
    pdf = fitz.open(input_file_path)
    docs = get_json_file_elements(input_json_path)
    
    for page_number in range(1, num_pages + 1):
        if progress:
            progress.update(progress.task_ids[0], description=f"Processing page {page_number}/{num_pages}", advance=1)
        
        page_docs = [doc for doc in docs if doc['metadata'].get('page_number') == page_number]
        plot_pdf_with_boxes(pdf.load_page(page_number - 1), page_docs, input_file_path, image_dir)
            
    pdf.close()
