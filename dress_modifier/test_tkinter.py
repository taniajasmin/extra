import torch
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from diffusers import StableDiffusionInpaintPipeline

class DressModifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dress Modifier")
        self.root.geometry("800x600")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.pipe = None
        self.load_model()
        
        self.image = None
        self.mask = None
        self.image_path = None
        self.mask_path = None
        
        self.setup_ui()
    
    def load_model(self):
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
    
    def setup_ui(self):
        # Title and Instructions
        tk.Label(self.root, text="Dress Modifier", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text="Upload a photo and mask, then describe the dress change.", font=("Arial", 10)).pack()
        
        # Buttons for uploading files
        tk.Button(self.root, text="Upload Photo", command=self.upload_photo, width=20).pack(pady=5)
        tk.Button(self.root, text="Upload Mask (Black on White for dress area)", command=self.upload_mask, width=30).pack(pady=5)
        
        # Text input for prompt
        tk.Label(self.root, text="Describe the dress change:", font=("Arial", 10)).pack(pady=5)
        self.prompt_entry = tk.Entry(self.root, width=50)
        self.prompt_entry.pack(pady=5)
        self.prompt_entry.insert(0, "e.g., red flowing evening dress")
        
        # Button to process the modification
        tk.Button(self.root, text="Modify Dress", command=self.modify_dress, width=20, bg="green", fg="white").pack(pady=10)
        
        # Status and Result Display
        self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Frame to show images (optional, basic preview)
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)
        self.image_label = tk.Label(self.image_frame, text="No image uploaded")
        self.image_label.pack(side=tk.LEFT, padx=10)
        self.result_label = tk.Label(self.image_frame, text="No result yet")
        self.result_label.pack(side=tk.LEFT, padx=10)
    
    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.image_path = file_path
            self.image = Image.open(file_path).convert('RGB')
            # Resize for preview (optional)
            preview_size = (200, 200)
            preview_img = self.image.copy()
            preview_img.thumbnail(preview_size)
            photo = ImageTk.PhotoImage(preview_img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            self.status_label.configure(text="Status: Photo uploaded")
    
    def upload_mask(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.mask_path = file_path
            self.mask = Image.open(file_path)
            self.status_label.configure(text="Status: Mask uploaded")
    
    def modify_dress(self):
        if self.image is None or self.mask is None:
            messagebox.showerror("Error", "Please upload both a photo and a mask image.")
            return
        
        if not self.prompt_entry.get():
            messagebox.showerror("Error", "Please provide a description for the dress change.")
            return
        
        prompt = self.prompt_entry.get()
        self.status_label.configure(text="Status: Processing...")
        self.root.update()
        
        if self.pipe is None:
            result, message = self.fallback_modify(self.image, self.mask, prompt)
        else:
            try:
                mask_image = self.mask.convert('L')
                fashion_prompt = f"{prompt}, fashion photography, detailed fabric, high quality"
                
                result = self.pipe(
                    prompt=fashion_prompt,
                    image=self.image,
                    mask_image=mask_image,
                    guidance_scale=7.5,
                    num_inference_steps=30,
                ).images[0]
                message = f"✅ Dress modified: {prompt}"
            except Exception as e:
                print(f"Error during dress modification: {e}")
                result, message = self.fallback_modify(self.image, self.mask, prompt)
        
        # Save result
        result_path = os.path.join(os.getcwd(), "result.png")
        result.save(result_path)
        
        # Show result preview (optional)
        preview_size = (200, 200)
        preview_result = result.copy()
        preview_result.thumbnail(preview_size)
        photo_result = ImageTk.PhotoImage(preview_result)
        self.result_label.configure(image=photo_result, text="")
        self.result_label.image = photo_result  # Keep a reference
        
        self.status_label.configure(text=f"Status: {message}")
        messagebox.showinfo("Success", f"Result saved as 'result.png' at {result_path}")
    
    def fallback_modify(self, image, mask, prompt):
        print("Using fallback color modification")
        img_np = np.array(image)
        mask_np = np.array(mask.convert('L'))
        
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
        
        return Image.fromarray(img_np), "Fallback method applied due to model error"

if __name__ == "__main__":
    root = tk.Tk()
    app = DressModifierApp(root)
    root.mainloop()