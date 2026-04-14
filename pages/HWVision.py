import base64
import io
import json

import streamlit as st
from PIL import Image

from mydbtools import (
    connectMySQL,
    getVisionLLMModel,
    init_session_state,
    login_page,
    runSQL,
    show_connection_status,
)


def answer_query_on_image(aquestion, allm, aimage):
    with connectMySQL() as db:
        rows = runSQL(
            """
            select sys.ML_GENERATE(
                %s,
                JSON_OBJECT("model_id", %s, "image", %s)
            )
            """,
            db,
            (aquestion, allm, aimage),
        )
        return rows


def main():
    st.title("HeatWave demo Image using Visual LLM")
    show_connection_status()

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is None:
        st.info("Please upload an image file.")
        return

    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Uploaded Image", width="stretch")

        buffered = io.BytesIO()
        image.save(buffered, format=image.format or "PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()

        with st.expander("Show Base64 String"):
            st.code(img_base64, language="text")

    with col2:
        myquestion = st.text_input("Question about the image")
        llm_models = getVisionLLMModel()
        if not llm_models:
            st.error("No supported generation models were found for this connection.")
            return
        llm = st.selectbox("Choose LLM", llm_models)

        submitButton = st.button("Submit", width="stretch")
        if submitButton:
            if not myquestion.strip():
                st.warning("Enter a question.")
            else:
                ans = answer_query_on_image(myquestion, llm, img_base64)
                if ans:
                    response_json = json.loads(ans[0][0])
                    st.text_area("The image", response_json.get("text", ""), 400)


st.set_page_config(page_title="HeatWave Demo - Vision LLM", layout="wide")
init_session_state()

if not login_page():
    st.stop()

main()
