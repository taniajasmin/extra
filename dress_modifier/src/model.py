import torch
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
import numpy as np

class DressModifier:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.setup_model()
    
    def setup_model(self):
        """Setup inpainting model for dress modification"""
        try:
            print("Loading stabilityai/stable-diffusion-2-inpainting...")
            self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
                "stabilityai/stable-diffusion-2-inpainting",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                use_auth_token=False,
                safety_checker=None,
                requires_safety_checker=False
            )
            self.pipe = self.pipe.to(self.device)
            print("✅ Successfully loaded Stable Diffusion model")
        except Exception as e:
            print(f"❌ Model loading failed: {str(e)[:100]}...")
            print("Will use fallback method for dress modification.")
            self.pipe = None
    
    def modify_dress(self, image, mask, prompt):
        """Modify dress based on user prompt"""
        if self.pipe is None:
            return self.fallback_modify(image, mask, prompt)
        
        try:
            # Enhance prompt for better dress results
            dress_prompt = f"beautiful {prompt}, high fashion, elegant dress, professional photography, detailed fabric texture, realistic lighting"
            
            result = self.pipe(
                prompt=dress_prompt,
                image=image,
                mask_image=mask,
                guidance_scale=8.0,
                num_inference_steps=30,
                strength=0.95,
                negative_prompt="ugly, blurry, low quality, distorted, bad anatomy"
            ).images[0]
            
            return result
            
        except Exception as e:
            print(f"AI model failed: {e}")
            return self.fallback_modify(image, mask, prompt)
    
    def fallback_modify(self, image, mask, prompt):
        """Simple color/pattern change when AI fails"""
        print("Using fallback modification...")
        
        # Convert to numpy
        img_np = np.array(image)
        mask_np = np.array(mask)
        
        # Simple color modification based on prompt
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
        
        return Image.fromarray(img_np.astype(np.uint8))