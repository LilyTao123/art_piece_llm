import streamlit as st
import requests
import json

API_BASE = "https://5zny2nzif1.execute-api.us-east-1.amazonaws.com/dev"

st.title("The art you loved")

st.header("Upload the picture")

# 1) upload the picture
file = st.file_uploader("choose the format of picture", type=["jpg", "jpeg", "png"])

# 2) the information list
title = st.text_input("art title")
artist = st.text_input("artist")
year = st.number_input("created year", min_value=0, max_value=3000, step=1)
material = st.text_input("material")
size = st.text_input("size 50x70cm）")
description = st.text_area("description")
tags = st.text_input("tags")
notes = st.text_area("notes")

if st.button("Submit"):
    if not file:
        st.error("Please choose a picture")
        st.stop()

    st.info("Getting the url..")

    res = requests.get(API_BASE + "/get-upload-url")
    data = res.json()
    st.write(data)
    upload_url = data["upload_url"]
    image_url = data["image_url"]
    image_id = data["image_id"]

    st.info("Uploading picture to S3...")

    upload_res = requests.put(upload_url, data=file.getvalue())

    if upload_res.status_code != 200:
        st.error("Picture upload failed! ")
        st.write(upload_res.text)
        st.stop()

    st.success("Picture uploaded")

    art_info = {
        "id": image_id,  
        "title": title,
        "artist": artist,
        "createdyear": int(year),
        "material": material,
        "size": size,
        "description": description,
        "image_url": image_url,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "notes": notes
    }

    st.info("Saving the information...")

    save_res = requests.post(
        API_BASE + "/save-art",
        data=json.dumps(art_info)
    )

    if save_res.status_code == 200:
        st.success("Uploaded successfully！")
        st.write(art_info)
    else:
        st.error("Failed")
        st.write(save_res.text)
