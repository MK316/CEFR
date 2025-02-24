import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd
import numpy as np

# Define URLs for text files hosted on GitHub
urls = {
    'Level B': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt',
    'Level C': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRC1.txt'
}

def clean_word(word):
    return word.split()[0]  # Remove parts of speech or other annotations

@st.cache_data
def load_data(level):
    data = pd.read_csv(urls[level], sep='\t', usecols=['SID', 'WORD'])
    data['WORD'] = data['WORD'].apply(clean_word)
    return data

def main():
    st.title("Word Practice App")
    
    user_name = st.text_input("User name")
    level = st.radio("Select Level:", ['Level B', 'Level C'])
    data = load_data(level)

    # Create SID ranges (1-20, 21-40, etc.)
    max_sid = data['SID'].max()
    sid_ranges = [(i, min(i + 19, max_sid)) for i in range(1, max_sid + 1, 20)]
    selected_range = st.selectbox("Select SID Range:", sid_ranges, format_func=lambda x: f"{x[0]}-{x[1]}")
    selected_data = data[(data['SID'] >= selected_range[0]) & (data['SID'] <= selected_range[1])]

    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.correct_count = 0

    if st.button('Show next word'):
        if st.session_state.index < len(selected_data):
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
        else:
            st.session_state.index = 0  # Reset for possible restart or review
            if st.button('Show result'):
                st.write(f"{user_name}: {st.session_state.correct_count}/{len(selected_data)} correct.")

if __name__ == "__main__":
    main()
