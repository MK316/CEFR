import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with caching
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt'
    return pd.read_csv(url, sep='\t', usecols=['SID', 'WORD']).assign(WORD=lambda df: df['WORD'].str.split().str[0])

def main():
    st.title("Word Practice App")
    user_name = st.text_input("User name")
    data = load_data()

    start_sid = st.number_input("Start SID", min_value=1, max_value=data['SID'].max(), value=1)
    end_sid = st.number_input("End SID", min_value=1, max_value=data['SID'].max(), value=20)
    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)]

    if 'generated' not in st.session_state:
        st.session_state.generated = False

    generate_button = st.button('Generate Audio')
    if generate_button or st.session_state.generated:
        st.session_state.generated = True
        for i, row in enumerate(filtered_data.itertuples()):
            with st.container():
                key = f'audio_{i}'
                audio_data = generate_audio(row.WORD)
                st.audio(audio_data, format='audio/mp3', key=key)
                st.text_input("Type the word shown:", key=f'input_{i}')

    if st.button('Check Answers'):
        check_answers(filtered_data)

def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file

def check_answers(filtered_data):
    correct_count = 0
    for i, row in enumerate(filtered_data.itertuples()):
        user_input = st.session_state.get(f'input_{i}', '')
        correct = user_input.strip().lower() == row.WORD.lower()
        if correct:
            correct_count += 1
        st.write(f"Word: {row.WORD}, Your Input: {user_input}, Correct: {correct}")
    st.write(f"{st.session_state.user_name}: {correct_count}/{len(filtered_data)} correct.")

if __name__ == "__main__":
    main()
