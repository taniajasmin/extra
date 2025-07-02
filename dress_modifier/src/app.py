import gradio as gr
from .model import DressModifier
from .utils import resize_image, mask_to_pil

class DressModifierApp:
    def __init__(self):
        self.modifier = DressModifier()
    
    def modify_dress_interface(self, image, mask_data, prompt):
        """Interface function for Gradio"""
        if image is None:
            return None, "❌ Please upload an image first"
        
        if mask_data is None:
            return None, "❌ Please draw on the dress area you want to change"
        
        if not prompt.strip():
            return None, "❌ Please write what you want to change (e.g., 'red flowing dress')"
        
        try:
            # Process inputs
            image = resize_image(image)
            mask = mask_to_pil(mask_data)
            
            # Modify the dress
            result = self.modifier.modify_dress(image, mask, prompt)
            
            return result, f"✅ Dress modified: {prompt}"
            
        except Exception as e:
            return None, f"❌ Error: {str(e)}"
    
    def build_interface(self):
        """Build and return the Gradio interface"""
        with gr.Blocks(title="AI Dress Modifier", theme=gr.themes.Soft()) as app:
            
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h1>👗 AI Dress Modifier</h1>
                <p>Upload a photo, mark the dress area, and describe how you want to change it!</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Input section
                    gr.HTML("<h3>📸 Upload & Edit</h3>")
                    
                    input_image = gr.Image(
                        label="Upload your photo",
                        type="pil",
                        height=400
                    )
                    
                    mask_editor = gr.ImageMask(
                        label="Draw on the dress area you want to change",
                        type="pil",
                        height=400
                    )
                    
                    prompt_input = gr.Textbox(
                        label="Describe the dress change",
                        placeholder="e.g., red flowing evening dress, blue floral summer dress, elegant black gown...",
                        lines=3
                    )
                    
                    modify_btn = gr.Button(
                        "✨ Modify Dress!", 
                        variant="primary",
                        size="lg"
                    )
                    
                with gr.Column(scale=1):
                    # Output section
                    gr.HTML("<h3>✨ Result</h3>")
                    
                    output_image = gr.Image(
                        label="Modified dress",
                        height=400
                    )
                    
                    status_text = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=2
                    )
                    
                    # Quick examples
                    gr.HTML("<h4>💡 Example prompts:</h4>")
                    gr.HTML("""
                    <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 12px;">
                    • "red flowing evening dress"<br>
                    • "blue floral summer dress"<br>
                    • "elegant black cocktail dress"<br>
                    • "white wedding gown with lace"<br>
                    • "colorful tie-dye maxi dress"
                    </div>
                    """)
            
            # Connect the function
            modify_btn.click(
                fn=self.modify_dress_interface,
                inputs=[input_image, mask_editor, prompt_input],
                outputs=[output_image, status_text]
            )
            
            # Example instructions
            gr.HTML("<br><h4>📝 How to use:</h4>")
            gr.HTML("""
            <ol style="font-size: 14px;">
                <li>Upload a photo with a person wearing a dress</li>
                <li>Use the drawing tool to mark the dress area</li>
                <li>Write what kind of dress you want (color, style, etc.)</li>
                <li>Click "Modify Dress!" and wait for the magic ✨</li>
            </ol>
            """)
        
        return app