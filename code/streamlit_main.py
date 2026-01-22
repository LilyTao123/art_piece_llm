import streamlit as st
from upload_art_info import page_upload_pic
from scan_art_get_info import page_scan_art

pages = {
    "Page 1": page_upload_pic,
    "Page 2": page_scan_art,
}

page = st.sidebar.selectbox("Select page", pages.keys())
pages[page]()
