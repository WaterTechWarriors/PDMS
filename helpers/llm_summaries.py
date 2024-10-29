"""
-----------------------------------------------------------------
(C) 2024 Prof. Tiran Dagan, FDU University. All rights reserved.
-----------------------------------------------------------------

LLM Image Summary Module

This module provides functionality to enhance JSON data with LLM-generated
summaries of images using OpenAI's GPT-4 Vision model.
"""

from openai import OpenAI
import json
from .config import global_config
import os
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .display import select_json_file

console = Console()

def enrich_json_with_summaries(json_file):
    """
    Processes JSON data, generating summaries for images that don't have them.
    
    Args:
        json_file (str): Path to the JSON file being processed.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Count unprocessed images
    images_to_process = [item for item in json_data 
                        if item['type'] == 'Image' and 'image_description' not in item['metadata']
                        ]
    total_images = len(images_to_process)
    
    if total_images == 0:
        console.print("No new images to process", style="yellow")
        return json_data

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(
            f"Processing images in {os.path.basename(json_file)}", 
            total=total_images
        )

        for item in images_to_process:
            image_base64 = item['metadata'].get('image_base64')
            if image_base64:
                try:
                    summary = summarize_image(image_base64)
                    #item['metadata']['image_description'] = summary
                    item['text'] = summary

                    # Save after each image is processed
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
                    progress.advance(task)
                except Exception as e:
                    console.print(f"Error processing image: {str(e)}", style="red")
                    logging.error(f"Error processing image: {str(e)}")
            else:
                console.print(f"Skipping image without base64 data: {item.get('text', 'Unnamed image')}", 
                            style="yellow")

    return

def summarize_image(image_base64):
    """
    Generates a summary of an image using OpenAI's GPT-4 Vision model.

    Args:
        image_base64 (str): Base64-encoded image data.

    Returns:
        str: A text summary of the image content.
    """
    client = OpenAI(api_key=global_config.get('API_KEYS', 'openai_api_key'))
    
    prompt = """You are an image summarizing agent. I will be giving you an image and you will provide a summary describing 
    the image, starting with "An image", or "An illustration", or "A diagram:", or "A logo:" or "A symbol:". If it contains a part, 
    you will try to identify the part and if it shows an action (such as a person cleaning 
    a pool or a woman holding a pool cleaning product) you will call those out. If it is a symbol, just give the symbol
    a meaningful name such as "warning symbol" or "attention!"
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def build_json_image_summaries():
    """Enhances images in JSON files with LLM-generated summaries."""
    output_dir = os.path.realpath(global_config.get('DIRECTORIES', 'output_dir'))
    partitioned_dir = os.path.join(output_dir, '01_partitioned')
    json_files = select_json_file(partitioned_dir)
    
    if not json_files:
        return
    
    for json_file in json_files:
        try:
            console.print(f"\nProcessing {os.path.basename(json_file)}...", style="blue")
            enrich_json_with_summaries(json_file)
            logging.info(f"Enhanced images in {json_file}")
        except Exception as e:
            console.print(f"Error processing {json_file}: {str(e)}", style="red")
            logging.error(f"Error processing {json_file}: {str(e)}")
