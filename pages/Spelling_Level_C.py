import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with caching
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/MK316/Engpro-Class/refs/heads/main/data/CEFRC1.txt' 
    return pd.read_csv(url, sep='\t', usecols=['SID', 'WORD']).assign(
        SID=lambda df: df['SID'].astype(int),  # <-- Fix: Convert "SID" column to integer
        WORD=lambda df: df['WORD'].str.split().str[0]
    )

def generate_audio(text):
    """Generate speech audio for a given text using gTTS."""
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()  # Return the byte content

def main():
    st.title("Word Practice App")
    user_name = st.text_input("User name")

    data = load_data()

    # Layout adjustment: Put Start SID and End SID in one row
    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input("Start SID", min_value=1, max_value=data['SID'].max(), value=1)
    with col2:
        end_sid = st.number_input("End SID", min_value=1, max_value=data['SID'].max(), value=min(start_sid + 19, data['SID'].max()))

    # Filter words based on selected SID range
    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)].reset_index(drop=True)

    # Ensure session state is initialized properly
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = {}

    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}

    if st.button('Generate Audio'):
        # Reset session state on new generation
        st.session_state.audio_data.clear()
        st.session_state.user_inputs.clear()  # Reset user inputs
        st.session_state.generated = True  

        # Initialize new user input fields
        for row in filtered_data.itertuples():
            sid_key = f'input_{row.SID}'
            st.session_state.user_inputs[sid_key] = ""  # Force reset inputs
            audio_key = f'audio_{row.SID}'  # Use SID directly to ensure uniqueness
            st.session_state.audio_data[audio_key] = generate_audio(row.WORD)

    if st.session_state.get('generated', False):
        for row in filtered_data.itertuples():
            audio_key = f'audio_{row.SID}'
            sid_key = f'input_{row.SID}'

            if audio_key in st.session_state.audio_data:
                st.caption(f"SID {row.SID}")  # Display SID before each audio
                st.audio(st.session_state.audio_data[audio_key], format='audio/mp3')

                # **Force reset user input fields using `value=""`**
                st.text_input("Type the word shown:", key=sid_key, value="", placeholder="Type here...", label_visibility="collapsed")

    if st.button('Check Answers'):
        correct_count = 0
        for row in filtered_data.itertuples():
            sid_key = f'input_{row.SID}'
            user_input = st.session_state.get(sid_key, '').strip().lower()
            correct = user_input == row.WORD.lower()
            if correct:
                correct_count += 1
            st.write(f"Word: {row.WORD}, Your Input: {user_input}, Correct: {correct}")

        st.write(f"{user_name}: {correct_count}/{len(filtered_data)} correct.")

if __name__ == "__main__":
    main()
