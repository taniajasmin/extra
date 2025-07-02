# from src.app import DressModifierApp

# if __name__ == "__main__":
#     app = DressModifierApp()
#     interface = app.build_interface()
#     interface.launch(
#         share=False,  
#         debug=True,
#         server_name="localhost",
#         server_port=7860
#     )


from src.app import DressModifierApp

if __name__ == "__main__":
    app = DressModifierApp()
    interface = app.build_interface()
    interface.launch(
        share=True,  # Enable public sharing to avoid localhost issues
        debug=True,
        server_name="localhost",
        server_port=7860
    )