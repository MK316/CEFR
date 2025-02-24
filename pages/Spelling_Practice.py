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
    data = load_data()

    max_sid = data['SID'].max()
    sid_ranges = [(i, min(i + 19, max_sid)) for i in range(1, max_sid + 1, 20)]
    selected_range = st.selectbox("Select SID Range:", sid_ranges, format_func=lambda x: f"{x[0]}-{x[1]}")
    filtered_data = data[(data['SID'] >= selected_range[0]) & (data['SID'] <= selected_range[1])]

    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.correct_count = 0

    if st.session_state.index < len(filtered_data):
        word = filtered_data.iloc[st.session_state.index]['WORD']
        tts = gTTS(text=word, lang='en')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        # Using simple key assignment for audio
        st.audio(audio_file, format='audio/mp3')
        user_input = st.text_input("Type the word shown:", key=f'input_{st.session_state.index}')

        if st.button('Next'):
            if user_input.strip().lower() == word.lower():
                st.session_state.correct_count += 1
            st.session_state.index += 1
    else:
        st.write(f"{user_name}: {st.session_state.correct_count}/{len(filtered_data)} correct.")
        if st.button('Restart'):
            st.session_state.index = 0
            st.session_state.correct_count = 0

if __name__ == "__main__":
    main()
