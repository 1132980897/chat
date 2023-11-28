import os
import wave
import numpy as np
import pyaudio
from pydub import AudioSegment
import streamlit as st
from pydub.playback import play
from utils import tts_ws_python3, iat_ws_python3,SparkApi
# 以下密钥信息从控制台获取
appid = "383202ee"  # 填写控制台中获取的 APPID 信息
api_secret = "YzFlMjNmMmE5MTExZTY1Y2JjNzRmNDgw"  # 填写控制台中获取的 APISecret 信息
api_key = "0bd22693b58a93adec0b724eab662f45"  # 填写控制台中获取的 APIKey 信息
domain = "generalv3"  # v2.0版本
Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v2.0环境的地址

text = []


def getText(role, content):
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while getlength(text) > 8000:
        del text[0]
    return text


def record_audio(filename, chunk, format, channels, rate, silence_duration):
    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    silence_frames = 0

    st.text("正在录音，请说话...")

    try:
        while True:
            data = stream.read(chunk)
            frames.append(data)

            # 将PCM数据转换为numpy数组以检测静音
            audio_data = np.frombuffer(data, dtype=np.int16)

            # 检查音频是否包含静音
            if np.max(np.abs(audio_data)) < 500:
                silence_frames += 1
            else:
                silence_frames = 0

            # 如果静音持续时间超过一定限制，则停止录音
            if silence_frames > silence_duration * rate / chunk:
                break

    except KeyboardInterrupt:
        pass

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    st.text("录音完成！")


def main():
    # 在 Streamlit 网页上显示欢迎文本
    st.title("💬 Chatbot")

    # 初始化对话历史和生成的响应列表
    st.session_state.setdefault('generated', [])
    st.session_state.setdefault('past', [])

    # 使用st.container创建水平容器
    container = st.container()

    # 输入文本框
    user_input = container.chat_input("请输入您的问题:", key='input')

    if container.button("开始录音"):

        record_audio(
            filename='./utils/user/chat.wav',
            chunk=1024,
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            silence_duration=1
        )

        user_input = iat_ws_python3.iat_ws("./utils/user/chat.wav")

    if user_input:
        # 构造用户输入的对话信息
        question = checklen(getText("user", user_input))

        # 调用 SparkApi 中的函数进行问题回答
        SparkApi.answer = ""
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        output = getText("assistant", SparkApi.answer)

        # 将用户输入和生成的响应添加到对话历史和生成的响应列表中
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(str(output[1]['content']))

        # 遍历对话历史和生成的响应
        for user_input, generated_response in zip(st.session_state['past'], st.session_state['generated']):
            st.chat_message("user").markdown(user_input)
            st.chat_message("assistant").markdown(generated_response)

        # 播放语音回答
        tts_ws_python3.main('"{}"'.format(generated_response))
        st.audio("./utils/user/demo.mp3")
        st.markdown(
            """
            <script>
                const audio = document.getElementById("audio");
                audio.autoplay = true;
            </script>
            """,
            unsafe_allow_html=True
        )

    if st.button("清空会话历史"):
        st.session_state['past'] = []  # 清空用户的历史输入
        st.session_state['generated'] = []

if __name__ == "__main__":

    st.set_page_config(
        page_icon="🤖",
        layout="centered",
    )
    main()
