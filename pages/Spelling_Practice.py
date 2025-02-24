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

    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.correct_count = 0

    if st.session_state.index < len(filtered_data):
        word = filtered_data.iloc[st.session_state.index]['WORD']
        tts = gTTS(text=word, lang='en')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        st.audio(audio_file, format='audio/mp3')

        user_input = st.text_input("Type the word shown:", key=f'input_{st.session_state.index}')

        if st.button('Next'):
            if user_input.strip().lower() == word.lower():
                st.session_state.correct_count += 1
            st.session_state.index += 1

    if st.session_state.index >= len(filtered_data) and 'displayed_feedback' not in st.session_state:
        st.write(f"{user_name}: {st.session_state.correct_count}/{len(filtered_data)} correct.")
        st.session_state.displayed_feedback = True
        if st.button('Restart'):
            st.session_state.index = 0
            st.session_state.correct_count = 0
            del st.session_state.displayed_feedback

if __name__ == "__main__":
    main()
