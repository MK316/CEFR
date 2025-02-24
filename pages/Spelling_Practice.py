import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with caching
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt'
    data = pd.read_csv(url, sep='\t', usecols=['SID', 'WORD'])
    data['WORD'] = data['WORD'].apply(lambda x: x.split()[0])  # Clean the words
    return data

def main():
    st.title("Word Practice App")
    user_name = st.text_input("User name")
    data = load_data()

    # SID range input
    start_sid = st.number_input("Start SID", min_value=1, max_value=data['SID'].max(), value=1, step=1)
    end_sid = st.number_input("End SID", min_value=1, max_value=data['SID'].max(), value=20, step=1)
    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)]

    # Session state setup
    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.correct_count = 0

    # Display word and handle input
    if st.session_state.index < len(filtered_data):
        word = filtered_data.iloc[st.session_state.index]['WORD']
        tts = gTTS(text=word, lang='en')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        
        st.audio(audio_file, format='audio/mp3', key=f'audio_{st.session_state.index}')
        user_input = st.text_input("Type the word shown:", key=f'input_{st.session_state.index}')
        
        if st.button('Next', key=f'next_{st.session_state.index}'):
            if user_input.strip().lower() == word.lower():
                st.session_state.correct_count += 1
            st.session_state.index += 1

    # Final feedback and restart option
    else:
        st.write(f"{user_name}: {st.session_state.correct_count}/{len(filtered_data)} correct.")
        if st.button('Restart'):
            st.session_state.index = 0
            st.session_state.correct_count = 0

if __name__ == "__main__":
    main()
