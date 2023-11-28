import os
import streamlit as st
import pyaudio
import wave
from utils import iat_ws_python3
import numpy as np

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



    tab1, tab2 = st.tabs(["# 🔵🟪🔶", "# 🟥◻🔻"])
    with tab1:
        st.title("录音应用")

        output_text = st.empty()

        output_text.text_area(" ", value=None, height=200)

        if st.button("开始录音"):
            record_audio(
                filename='./utils/user/output.wav',
                chunk=1024,
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                silence_duration=1
            )

            output = iat_ws_python3.iat_ws("./utils/user/output.wav")
            output_text.text_area("  ", value=output, height=200)

    with tab2:
        st.title("文件处理")

        output_text1 = st.empty()

        output_text1.text_area("输出", value=None, height=200)

        # 创建一个文件夹用于保存上传的文件
        if not os.path.exists("./utils/uploads"):
            os.makedirs("./utils/uploads")

        # 选择文件并重命名
        file_name = st.text_input("文件名")
        uploaded_file = st.file_uploader("选择文件", type="wav")

        # 保存文件
        if uploaded_file is not None:
            if file_name.strip():
                file_name_with_extension = file_name + ".wav"
                file_path = os.path.join("./utils/uploads", file_name_with_extension)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"已保存文件: {file_path}")

                # 获取当前工作目录并打印
                current_directory = os.getcwd()
                full_file_path = os.path.join(current_directory, file_path)
                st.write(f"{full_file_path}")
            else:
                st.error("请命名文件")
            output1 = iat_ws_python3.iat_ws(rf"{full_file_path}")
            output_text1.text_area(" ", value=output1, height=200)

if __name__ == "__main__":

    st.set_page_config(
        page_title="3",
        page_icon="🤡",
        layout="centered",
    )
    main()

