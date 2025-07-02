import torch
import numpy as np
from PIL import Image
import gradio as gr
from diffusers import StableDiffusionInpaintPipeline

class SimpleDressModifier:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        try:
            print("Loading Stable Diffusion model...")
            self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
                "stabilityai/stable-diffusion-2-inpainting",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            ).to(self.device)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.pipe = None
    
    def modify_dress(self, image, mask, prompt):
        if image is None or mask is None:
            return None, "Please provide both image and mask"
        
        if self.pipe is None:
            return self.fallback_modify(image, mask, prompt), "Using fallback method (AI model failed to load)"
        
        try:
            if isinstance(mask, dict) and 'mask' in mask:
                mask_image = Image.fromarray(mask['mask']).convert('L')
            else:
                mask_image = Image.fromarray(mask).convert('L')
            
            fashion_prompt = f"{prompt}, fashion photography, detailed fabric, high quality"
            
            result = self.pipe(
                prompt=fashion_prompt,
                image=image,
                mask_image=mask_image,
                guidance_scale=7.5,
                num_inference_steps=30,
            ).images[0]
            
            return result, f"✅ Dress modified: {prompt}"
        
        except Exception as e:
            print(f"Error during dress modification: {e}")
            return self.fallback_modify(image, mask, prompt), f"Using fallback method: {str(e)}"
    
    def fallback_modify(self, image, mask, prompt):
        print("Using fallback color modification")
        img_np = np.array(image)
        
        if isinstance(mask, dict) and 'mask' in mask:
            mask_np = mask['mask']
        else:
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

# Create minimal interface
def create_minimal_app():
    modifier = SimpleDressModifier()
    
    def process(input_img, mask_img, prompt):
        if input_img is None:
            return None, "Please upload an image"
        if mask_img is None:
            return None, "Please upload a mask image"
        if not prompt:
            return None, "Please describe the dress change"
            
        result, message = modifier.modify_dress(input_img, mask_img, prompt)
        return result, message
    
    interface = gr.Interface(
        fn=process,
        inputs=[
            gr.Image(label="Upload Photo", type="pil"),
            gr.Image(label="Upload Mask (Draw on dress area)", type="numpy"),
            gr.Textbox(label="Describe the change", placeholder="e.g., red flowing dress")
        ],
        outputs=[
            gr.Image(label="Result"),
            gr.Textbox(label="Status")
        ],
        title="Dress Modifier",
        description="Upload a photo and a mask image (drawn separately) to modify the dress."
    )
    
    return interface

if __name__ == "__main__":
    app = create_minimal_app()
    app.launch(share=True, debug=True)