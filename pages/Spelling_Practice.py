import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

def clean_word(word):
    return word.split()[0]  # Clean the word to remove parts of speech annotations

def load_data(level):
    urls = {
        'Level B': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt',
        'Level C': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRC1.txt'
    }
    data = pd.read_csv(urls[level], sep='\t', usecols=['SID', 'WORD'])
    data['WORD'] = data['WORD'].apply(clean_word)
    return data

def initialize_state():
    if 'index' not in st.session_state:
        st.session_state.index = 0
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0

def main():
    st.title("Word Practice App")

    user_name = st.text_input("User name")
    level = st.radio("Select Level:", ['Level B', 'Level C'])
    data = load_data(level)

    max_sid = data['SID'].max()
    sid_ranges = [(i, min(i + 19, max_sid)) for i in range(1, max_sid + 1, 20)]
    selected_range = st.selectbox("Select SID Range:", sid_ranges, format_func=lambda x: f"{x[0]}-{x[1]}")
    selected_data = data[(data['SID'] >= selected_range[0]) & (data['SID'] <= selected_range[1])]

    initialize_state()

    if st.button('Show next word') and st.session_state.index < len(selected_data):
        word = selected_data.iloc[st.session_state.index]['WORD']
        tts = gTTS(text=word, lang='en')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        st.audio(audio_file, format='audio/mp3')
        user_input = st.text_input("Type the word shown:", key=f'word_{st.session_state.index}')

        if st.button('Next', key=f'next_{st.session_state.index}'):
            correct = user_input.strip().lower() == word.lower()
            if correct:
                st.session_state.correct_count += 1
            st.session_state.index += 1

    if st.session_state.index >= len(selected_data) and st.button('Show result'):
        st.write(f"{user_name}: {st.session_state.correct_count}/{len(selected_data)} correct.")
        st.session_state.index = 0  # Reset index for possible restart

if __name__ == "__main__":
    main()
