import streamlit as st
from elevenlabs import generate, play, set_api_key
import base64
from streamlit_mic_recorder import mic_recorder, speech_to_text
import numpy as np
from bokeh.models import ColumnDataSource, Button
from bokeh.plotting import figure, curdoc
from bokeh.driving import count
import asyncio
import threading
import requests

# Function to update the waveform in real-time
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
        st.markdown(
            md,
            unsafe_allow_html=True,
        )
# Function to plot audio waveform



# Voiceflow API key and user ID
voiceflow_api_key = "VF.DM.65409de36a2a5400076127f1.1AQK0cCvvWnOQziJ"
user_id = "user_123"
st.session_state._last_audio_id = 0

# Set Eleven Labs API key
set_api_key("1d54c6fcb21466e4e325552537e3d799")

# Streamlit app
st.title("Talk to OASIS")

st.image(image='oasis-mecha.png',caption='OASIS')
# User input

# Voice options
voice = "kFoByongNmtXS5dmvcJw"  # Set the default voice

state= st.session_state


if 'text_received' not in state:
    state.text_received=[]

c1,c2=st.columns(2)
with c1:
    st.write("Click to start talking and click again once done:")
with c2:
    text=speech_to_text(start_prompt="⏺️",stop_prompt="⏹️", language='en',use_container_width=True,just_once=True,key='STT')

if text:
    state.text_received.append(text)

# Ensure that there's at least one text received
if state.text_received:
    # Get the latest user input
    user_input = state.text_received[-1]
    st.write(user_input)
    chart_placeholder = st.empty()

    try:
        # Send user input to Voiceflow
        body = {"action": {"type": "text", "payload": user_input}}
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
        st.text("Oasis Response:")
        st.write(chatbot_response)
        print(chatbot_response)

        # Generate and play the audio using Eleven Labs API
        audio = generate(text=chatbot_response, voice=voice, model='eleven_multilingual_v1', api_key="1d54c6fcb21466e4e325552537e3d799")
        play(audio, notebook=True)

        # Convert the audio to base64 for streaming
        audio_base64 = base64.b64encode(audio).decode('utf-8')
        audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
        st.markdown(audio_tag, unsafe_allow_html=True)

        # Create a Bokeh plot for the waveform
        waveform_source = ColumnDataSource(data=dict(time=[], amplitude=[]))
        waveform_plot = figure(width=800, height=300, title="Audio Waveform", tools="pan,box_zoom,reset")
        waveform_plot.line('time', 'amplitude', source=waveform_source)

        # Call the update_waveform function in the Bokeh plot
        curdoc().add_periodic_callback(lambda: update_waveform(None, waveform_source, user_input), 100)

        chart_placeholder.bokeh_chart(waveform_plot)

        # Start the asyncio event loop in a separate thread
        loop_thread = threading.Thread(target=start_event_loop)
        loop_thread.start()

    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")


