import streamlit as st
from elevenlabs import generate, play, set_api_key
import base64
from streamlit_mic_recorder import mic_recorder, speech_to_text
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.driving import count
import asyncio
import threading
import requests

# Function to update the waveform in real-time
@count()
def update_waveform(n, waveform_source, user_input):
    # You need to implement a way to get real-time audio data for the waveform plot
    # For simplicity, I'm using a sinusoidal wave as an example
    time = np.linspace(0, 1, 1000)
    amplitude = np.sin(2 * np.pi * 5 * time)  # Example: 5 Hz sinusoidal wave

    waveform_source.stream(dict(time=time, amplitude=amplitude), rollover=1000)

# Function to start the asyncio event loop
def start_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Voiceflow API key and user ID
voiceflow_api_key = "VF.DM.65409de36a2a5400076127f1.1AQK0cCvvWnOQziJ"
user_id = "user_123"
st.session_state._last_audio_id = 0

# Set Eleven Labs API key
set_api_key("1d54c6fcb21466e4e325552537e3d799")

# Streamlit app
st.markdown(
    """
    <style>
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            font-size: 24px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<b><p class="centered">TALK TO OASIS</p></b>', unsafe_allow_html=True)

# Create layout columns
col1, col2, col3 = st.columns([3, 3, 6])

# Column 1: Image
col1.image(image='oasis-mecha.png')

# Column 2: Play/Stop button (centered)
with col2:
    text = speech_to_text(start_prompt="⏺️", stop_prompt="⏹️", language='en', use_container_width=True, just_once=True, key='STT')
    st.write("Click to start talking and click again once done.")

# Column 3: Chat area
with col3:
    st.text("Oasis Response:")
    if text:
        # Send user input to Voiceflow
        body = {"action": {"type": "text", "payload": text}}
        response = requests.post(
            f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact",
            json=body,
            headers={"Authorization": voiceflow_api_key},
        )

        # Extract chatbot response from Voiceflow

        # Extracting the 'payload' field from the second item in the list
        payload = response.json()[1]['payload']

        # Extracting the 'slate' field from the 'payload'
        slate = payload['slate']

        # Extracting the 'content' field from the 'slate'
        content = slate['content']
        chatbot_response = ""

        for j in range(len(content)):
            # Extracting the 'text' field from the 'content'
            text = content[j]['children'][0]['text']

            # Concatenate the extracted text to the chatbot response string
            chatbot_response += text + " "

        # Display chatbot response
        st.write(chatbot_response)
        print(chatbot_response)

        # Generate and play the audio using Eleven Labs API
        audio = generate(text=chatbot_response, voice='kFoByongNmtXS5dmvcJw', model='eleven_multilingual_v1', api_key="1d54c6fcb21466e4e325552537e3d799")
        play(audio, notebook=True)

        # Convert the audio to base64 for streaming
        audio_base64 = base64.b64encode(audio).decode('utf-8')
        audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
        st.markdown(audio_tag, unsafe_allow_html=True)



        # Start the asyncio event loop in a separate thread
        loop_thread = threading.Thread(target=start_event_loop)
        loop_thread.start()

