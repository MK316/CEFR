import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with the recommended caching
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
    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)].reset_index(drop=True)

    # Handling audio generation
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = {}

    generate_button = st.button('Generate Audio')
    if generate_button or 'generated' not in st.session_state:
        st.session_state.generated = True  # Flag to indicate generation was done
        # Clear existing audio data to regenerate it for new SID range
        st.session_state.audio_data = {}
        for i, row in enumerate(filtered_data.itertuples()):
            # Generate and store audio
            audio_key = f'audio_{start_sid + i}'
            tts = gTTS(text=row.WORD, lang='en')
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            st.session_state.audio_data[audio_key] = audio_file.getvalue()

    if st.session_state.get('generated', False):
        for i in range(len(filtered_data)):
            audio_key = f'audio_{start_sid + i}'
            st.audio(st.session_state.audio_data[audio_key], format='audio/mp3')
            st.text_input("Type the word shown:", key=f'input_{start_sid + i}')

    if st.button('Check Answers'):
        correct_count = 0
        for i in range(len(filtered_data)):
            user_input = st.session_state.get(f'input_{start_sid + i}', '')
            word = filtered_data.iloc[i]['WORD']
            correct = user_input.strip().lower() == word.lower()
            if correct:
                correct_count += 1
            st.write(f"Word: {word}, Your Input: {user_input}, Correct: {correct}")

        st.write(f"{user_name}: {correct_count}/{len(filtered_data)} correct.")

if __name__ == "__main__":
    main()
