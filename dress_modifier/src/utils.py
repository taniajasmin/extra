from PIL import Image
import numpy as np

def resize_image(image, max_size=512):
    """Resize image to prevent memory issues while maintaining aspect ratio"""
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return image

def mask_to_pil(mask_data):
    """Convert Gradio mask data to PIL Image"""
    if isinstance(mask_data, dict) and 'mask' in mask_data:
        return Image.fromarray(mask_data['mask']).convert('L')
    return mask_data