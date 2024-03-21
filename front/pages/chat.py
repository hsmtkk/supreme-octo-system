import os
import requests
import streamlit as st

chat_api = os.environ["CHAT_API"]

with st.form("form"):
    question = st.text_area("Question")
    submit_clicked = st.form_submit_button("Submit")

if submit_clicked:
    data = {
        "question": question,
    }
    answer = requests.post(chat_api, json=data)
    st.write(answer)
    st.json(answer)
