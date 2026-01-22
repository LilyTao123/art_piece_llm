import streamlit as st
import requests
import json
import cv2
import numpy as np
import uuid
from PIL import Image

from index import generate_image_embedding, save_image_index, search_nearest_image


def page_upload_pic():
    API_BASE = "https://5zny2nzif1.execute-api.us-east-1.amazonaws.com/dev"
    orb = cv2.ORB_create()

    headers={
            "Content-Type": "application/json"
        }

    st.title("The art you loved")

    st.header("Upload the picture")

    # 1) upload the picture
    file = st.file_uploader("choose the format of picture", type=["jpg", "jpeg", "png"])

    # 2) the information list
    title = st.text_input("art title")
    artist = st.text_input("artist")
    year = st.number_input("created year", min_value=0, max_value=3000, step=1)
    material = st.text_input("material")
    location = st.text_input("location")
    size = st.text_input("size 50x70cm）")
    description = st.text_area("description")
    tags = st.text_input("tags")

    art_info1 = {
            "title": title,
            "artist": artist,
            "createdyear": int(year),  
    }

    if st.button("Submit"):
        if not file:
            st.error("Please choose a picture")
            st.stop()

        st.info("Getting the url..")

        res = requests.post(API_BASE + "/get-upload-url", 
                            data = json.dumps(art_info1),
                            headers = headers)
        data = res.json()
        upload_url = data["upload_url"]
        image_url = data["image_url"]
        artwork_id = data["artwork_id"]

        st.info("Uploading picture to S3...")

        upload_res = requests.put(upload_url, data=file.getvalue())

        if upload_res.status_code != 200:
            st.error("Picture upload failed! ")
            st.write(upload_res.text)
            st.stop()

        st.success("Picture uploaded")

        art_info = {
            "id": artwork_id,  
            "title": title,
            "artist": artist,
            "createdyear": int(year),
            "material": material,
            "location": location,
            "size": size,
            "description": description,
            "image_url": image_url,
            "tags": [t.strip() for t in tags.split(",")] if tags else []
            # "descriptors": descriptors
        }

        st.info("Saving the information...")

        save_res = requests.post(
            API_BASE + "/save-art",
            data=json.dumps(art_info), headers = headers
        )
        res_body = save_res.json()
        

        if save_res.status_code == 200:
            st.success("Uploaded successfully！")
            image_id = res_body["item"]["seqId"]
            image = Image.open(file).convert("RGB")
            embd = generate_image_embedding(image)    
            save_image_index(embd, image_id)
        else:
            st.error("Failed")
            st.write(save_res.text)

