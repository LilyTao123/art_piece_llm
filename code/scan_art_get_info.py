import streamlit as st
from PIL import Image
import requests
from index import generate_image_embedding, save_image_index, search_nearest_image

API_BASE = "https://5zny2nzif1.execute-api.us-east-1.amazonaws.com/dev"

headers={
            "Content-Type": "application/json"
        }


def page_scan_art():
    st.header("Upload the picture")

    # 1) upload the picture
    file = st.file_uploader("choose the format of picture", type=["jpg", "jpeg", "png"])

    if st.button("Submit"):
        if not file:
            st.error("Please choose a picture")
            st.stop()
        image = Image.open(file).convert("RGB")
        embd = generate_image_embedding(image)
        seq_id = search_nearest_image(embd, k=1)
        st.write(seq_id)
        res = requests.get(API_BASE + "/art",
                    headers=headers,
                    params={"id": seq_id})
        data = res.json()
        st.write(data[0])
