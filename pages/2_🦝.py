import streamlit as st
from utils import tts_ws_python3

def main():


    st.title("文本转语音应用")


    input_text = st.empty()
    # 输入文本
    input_text = st.text_area("输入文本",height=200)

    # 按钮生成语音
    if st.button("生成语音"):

        if input_text:
            tts_ws_python3.main('"{}"'.format(input_text))
            st.audio("./utils/user/demo.mp3")

if __name__ == "__main__":

    st.set_page_config(
        page_title="2",
        page_icon="😺",
        layout="centered",
    )
    main()
