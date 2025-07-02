import torch
import cv2
import numpy as np
from PIL import Image
import gradio as gr
from diffusers import StableDiffusionInpaintPipeline

class SimpleDressModifier:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        try:
            # Load local model - no API key needed
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
        """Apply dress modification based on the mask and prompt"""
        if image is None or mask is None:
            return None, "Please provide both image and mask"
        
        if self.pipe is None:
            return self.fallback_modify(image, mask, prompt), "Using fallback method (AI model failed to load)"
        
        try:
            # Process inputs
            if isinstance(mask, dict) and 'mask' in mask:
                mask_array = mask['mask']
                mask_image = Image.fromarray(mask_array).convert('L')
            else:
                mask_image = Image.fromarray(mask).convert('L')
            
            # Add fashion-specific terms to prompt
            fashion_prompt = f"{prompt}, fashion photography, detailed fabric, high quality"
            
            # Run inference
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
        """Simple color modification when AI fails"""
        print("Using fallback color modification")
        
        # Convert to numpy arrays
        img_np = np.array(image)
        
        # Get mask array
        if isinstance(mask, dict) and 'mask' in mask:
            mask_np = mask['mask']
        else:
            mask_np = np.array(mask)
        
        # Simple color change based on prompt
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
            color = [200, 150, 200]  # Default purple
        
        # Apply color to masked area
        for i in range(3):
            img_np[:,:,i] = np.where(mask_np > 128, 
                                   img_np[:,:,i] * 0.3 + color[i] * 0.7, 
                                   img_np[:,:,i])
        
        return Image.fromarray(img_np)

# Create interface
def create_app():
    modifier = SimpleDressModifier()
    
    def process(input_img, mask_data, prompt):
        if input_img is None:
            return None, "Please upload an image"
        if mask_data is None or (isinstance(mask_data, dict) and mask_data.get('mask') is None):
            return None, "Please draw on the dress area"
        if not prompt:
            return None, "Please describe the dress change"
            
        result, message = modifier.modify_dress(input_img, mask_data, prompt)
        return result, message
    
    with gr.Blocks(title="Dress Modifier", theme=gr.themes.Base()) as app:
        gr.Markdown("# 👗 Dress Modifier")
        gr.Markdown("Upload a photo, mark the dress, and describe how you want to change it")
        
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(label="Upload Photo", type="pil")
                mask_input = gr.Sketchpad(
                    label="Draw on the dress area",
                    type="numpy",
                    image_mode="RGB",
                    brush=gr.Brush(default_size=20, colors=["#000000"])
                )
                prompt = gr.Textbox(label="Describe the change", placeholder="e.g., red flowing dress")
                submit_btn = gr.Button("Modify Dress", variant="primary")
            
            with gr.Column():
                output_image = gr.Image(label="Result")
                status = gr.Textbox(label="Status")
        
        submit_btn.click(
            fn=process,
            inputs=[input_image, mask_input, prompt],
            outputs=[output_image, status]
        )
        
        gr.Markdown("## How to use:")
        gr.Markdown("""
        1. Upload a photo with a dress
        2. Draw on the dress area you want to change (use the sketch tool)
        3. Describe how you want to change it
        4. Click "Modify Dress"
        """)
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(share=True)