import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

def clean_word(word):
    # Remove parts of speech or any characters following a space
    cleaned_word = re.sub(r'\s+.*', '', word)
    return cleaned_word

def load_data(level):
    data = pd.read_csv(urls[level], sep='\t', usecols=['SID', 'WORD'])
    # Clean each word in the dataframe
    data['WORD'] = data['WORD'].apply(clean_word)
    return data

def main():
    st.title("Word Practice App")
    
    user_name = st.text_input("User name")
    level = st.radio("Select Level:", list(urls.keys()))
    data = load_data(level)

    if 'index' not in st.session_state:
        st.session_state.index = 0

    selected_data = data.iloc[st.session_state.index: st.session_state.index + 1]

    if st.button("Show next word"):
        if st.session_state.index < len(data) - 1:
            st.session_state.index += 1
        selected_data = data.iloc[st.session_state.index: st.session_state.index + 1]
        word = selected_data.iloc[0]['WORD']
        tts = gTTS(text=word, lang='en')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        st.audio(audio_file, format='audio/mp3')
        user_input = st.text_input("Type the word shown:", key=st.session_state.index)
        if user_input:
            correct = "Correct" if user_input.strip().lower() == word.lower() else "Incorrect"
            st.write(f"{word} - {correct}")

    if st.button("Complete"):
        st.write(f"{user_name}: Score goes here")  # Implement scoring logic

if __name__ == "__main__":
    main()
