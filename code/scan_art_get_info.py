import streamlit as st
from PIL import Image

def page_scan_art():
    st.header("Upload the picture")

    # 1) upload the picture
    file = st.file_uploader("choose the format of picture", type=["jpg", "jpeg", "png"])
    image = Image.open(file).convert("RGB")
