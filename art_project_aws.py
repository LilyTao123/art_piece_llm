import streamlit as st
import requests
import json

API_BASE = "https://5zny2nzif1.execute-api.us-east-1.amazonaws.com/dev"

st.title("艺术品管理系统（Streamlit）")

st.header("上传艺术品")

# 1) 图片上传（本地先上传）
file = st.file_uploader("选择图片文件", type=["jpg", "jpeg", "png"])

# 2) 艺术品信息表单
title = st.text_input("艺术品名称")
artist = st.text_input("艺术家")
year = st.number_input("年份", min_value=0, max_value=3000, step=1)
material = st.text_input("材质")
size = st.text_input("尺寸（如 50x70cm）")
description = st.text_area("描述")
tags = st.text_input("标签（用逗号隔开）")
notes = st.text_area("备注")

if st.button("提交"):
    if not file:
        st.error("请先选择一张图片！")
        st.stop()

    st.info("正在获取上传链接...")

    # Step 1: 调用 get-upload-url API
    res = requests.get(API_BASE + "/get-upload-url")
    data = res.json()
    st.write(data)
    upload_url = data["upload_url"]
    file_key = data["fileKey"]

    st.info("正在上传图片到 S3...")

    # Step 2: 把图片 PUT 到预签名 URL
    headers = {"Content-Type": file.type}
    upload_res = requests.put(upload_url, data=file.getvalue(), headers=headers)

    if upload_res.status_code != 200:
        st.error("图片上传失败")
        st.write(upload_res.text)
        st.stop()

    st.success("图片上传成功！")

    # Step 3: 构建艺术品记录 JSON
    art_info = {
        "id": file_key,  # 用图片文件名作为 ID 也可以
        "title": title,
        "artist": artist,
        "year": int(year),
        "material": material,
        "size": size,
        "description": description,
        "image_url": f"https://artwork-info-app.s3.amazonaws.com/{file_key}",
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "notes": notes
    }

    st.info("正在保存艺术品信息到数据库...")

    # Step 4: 提交 save-art API
    save_res = requests.post(
        API_BASE + "/save-art",
        data=json.dumps(art_info)
    )

    if save_res.status_code == 200:
        st.success("艺术品上传成功！")
        st.write(art_info)
    else:
        st.error("保存失败")
        st.write(save_res.text)
