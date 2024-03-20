import base64
import os
import requests
import streamlit as st

upload_api = os.environ["UPLOAD_API"]

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    encoded = base64.b64encode(bytes_data)
    resp = requests.post(upload_api, data=encoded)
    if resp.status_code == 200:
        st.info("Upload done")
    else:
        st.error("Upload failed")