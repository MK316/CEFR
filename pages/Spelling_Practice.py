import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# URL for Level B file hosted on GitHub
url = 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt'

@st.cache_data
def load_data():
    data = pd.read_csv(url, sep='\t', usecols=['SID', 'WORD'])
    data['WORD'] = data['WORD'].apply(lambda x: x.split()[0])  # Clean the words
    return data

def main():
    st.title("Word Practice App")
    user_name = st.text_input("User name")

    if 'words_total' not in st.session_state:
        data = load_data()
        st.session_state.words_total = len(data)

    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.correct_count = 0

    if st.session_state.index < st.session_state.words_total:
        word = data.iloc[st.session_state.index]['WORD']
        tts = gTTS(text=word, lang='en')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        st.audio(audio_file, format='audio/mp3')
        user_input = st.text_input("Type the word shown:", key=f'word_{st.session_state.index}')

        if st.button('Next', key=f'next_{st.session_state.index}'):
            if user_input.strip().lower() == word.lower():
                st.session_state.correct_count += 1
            st.session_state.index += 1
    else:
        st.write(f"{user_name}: {st.session_state.correct_count}/{st.session_state.words_total} correct.")
        if st.button('Restart'):
            st.session_state.index = 0
            st.session_state.correct_count = 0

if __name__ == "__main__":
    main()
