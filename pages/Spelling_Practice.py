import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

def load_data(level):
    urls = {
        'Level B': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt',
        'Level C': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRC1.txt'
    }
    return pd.read_csv(urls[level], sep='\t', usecols=['SID', 'WORD'])

def clean_word(word):
    # Clean the word to remove parts of speech annotations
    return word.split()[0]

@st.cache(allow_output_mutation=True)
def get_data(level):
    data = load_data(level)
    data['WORD'] = data['WORD'].apply(clean_word)
    return data

def main():
    st.title("Word Practice App")
    
    user_name = st.text_input("User name")
    level = st.radio("Select Level:", ['Level B', 'Level C'])
    data = get_data(level)

    max_sid = data['SID'].max()
    sid_range = range(1, max_sid + 1)
    selected_sid = st.select_slider("Select SID Range:", options=sid_range)

    selected_data = data[data['SID'] == selected_sid]
    
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
            next_button = st.button('Next', key=f'next_{st.session_state.index}')
            
            if next_button:
                correct = user_input.strip().lower() == word.lower()
                if correct:
                    st.session_state.correct_count += 1
                st.session_state.index += 1
        else:
            st.session_state.index = 0  # Reset for possible restart or review
            st.button('Show result')

    if st.button('Show result'):
        st.write(f"{user_name}: {st.session_state.correct_count}/{len(selected_data)} correct.")

if __name__ == "__main__":
    main()
