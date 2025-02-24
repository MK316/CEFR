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

    if 'answers' not in st.session_state:
        st.session_state.answers = [None] * len(filtered_data)

    if st.button('Generate Audio'):
        for i, row in enumerate(filtered_data.itertuples()):
            tts = gTTS(text=row.WORD, lang='en')
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            st.audio(audio_file, format='audio/mp3', key=f'audio_{i}')
            st.text_input("Type the word shown:", key=f'input_{i}')

    if st.button('Check Answers'):
        correct_count = 0
        for i, row in enumerate(filtered_data.itertuples()):
            user_input = st.session_state[f'input_{i}']
            if user_input.strip().lower() == row.WORD.lower():
                correct_count += 1
            st.write(f"Word: {row.WORD}, Your Input: {user_input}, Correct: {user_input.strip().lower() == row.WORD.lower()}")

        st.write(f"{user_name}: {correct_count}/{len(filtered_data)} correct.")

if __name__ == "__main__":
    main()
