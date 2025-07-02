import torch
import numpy as np
from PIL import Image
import os
from diffusers import StableDiffusionInpaintPipeline

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    try:
        print("Loading Stable Diffusion model...")
        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-inpainting",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        ).to(device)
        print("✅ Model loaded successfully")
        return pipe, device
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None, device

def modify_dress(image_path, mask_path, prompt, pipe, device):
    if not os.path.exists(image_path) or not os.path.exists(mask_path):
        return None, "Image or mask file not found"
    
    image = Image.open(image_path).convert('RGB')
    mask = Image.open(mask_path).convert('L')
    
    if pipe is None:
        return fallback_modify(image, mask, prompt), "Using fallback method (AI model failed to load)"
    
    try:
        fashion_prompt = f"{prompt}, fashion photography, detailed fabric, high quality"
        result = pipe(
            prompt=fashion_prompt,
            image=image,
            mask_image=mask,
            guidance_scale=7.5,
            num_inference_steps=30,
        ).images[0]
        return result, f"✅ Dress modified: {prompt}"
    except Exception as e:
        print(f"Error during dress modification: {e}")
        return fallback_modify(image, mask, prompt), f"Using fallback method: {str(e)}"

def fallback_modify(image, mask, prompt):
    print("Using fallback color modification")
    img_np = np.array(image)
    mask_np = np.array(mask)
    
    if "red" in prompt.lower():
        color = [255, 100, 100]
    elif "blue" in prompt.lower():
        color = [100, 100, 255]
    elif "green" in prompt.lower():
        color = [100, 255, 100]
    elif "black" in prompt.lower():
        color = [50, 50, 50]
    elif "white" in prompt.lower():
        color = [240, 240, 240]
    else:
        color = [200, 150, 200]
    
    for i in range(3):
        img_np[:,:,i] = np.where(mask_np > 128, 
                               img_np[:,:,i] * 0.3 + color[i] * 0.7, 
                               img_np[:,:,i])
    
    return Image.fromarray(img_np)

if __name__ == "__main__":
    pipe, device = load_model()
    
    image_path = input("Enter the path to your image file (e.g., image.jpg): ")
    mask_path = input("Enter the path to your mask file (black on white for dress area, e.g., mask.png): ")
    prompt = input("Describe how you want to change the dress (e.g., red flowing dress): ")
    
    result, message = modify_dress(image_path, mask_path, prompt, pipe, device)
    print(message)
    
    if result is not None:
        result_path = "result.png"
        result.save(result_path)
        print(f"Result saved as {result_path}")
    else:
        print("Failed to modify dress.")