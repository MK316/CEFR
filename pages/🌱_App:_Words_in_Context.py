import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd
import hashlib

@st.cache(allow_output_mutation=True)  # Ensure data is loaded once and stored correctly across runs
def load_data(file_url):
    sep = ',' if file_url.endswith('.csv') else '\t'
    try:
        df = pd.read_csv(file_url, sep=sep)
        df.columns = [col.strip() for col in df.columns]  # Ensure columns are trimmed of whitespace
        df['SID'] = df['SID'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        raise

def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()

def main():
    st.markdown("### 🎧 CEFR Listen & Spell Practice")
    st.caption("Explore different levels of vocabulary through listening.")

    tab1, tab2 = st.tabs(["Level B", "Level C"])

    with tab1:
        data_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2WICf.csv"
        run_practice_app("LevelB", data_url)

    with tab2:
        data_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1WICf.csv"
        run_practice_app("LevelC", data_url)

def run_practice_app(level, file_url):
    data = load_data(file_url)
    if data is None:
        st.write("No data loaded.")
        return

    # Audio Generation
    if st.button(f'Generate Audio for {level}'):
        for index, row in data.iterrows():
            audio_key = f"audio_{level}_{row['SID']}"
            if audio_key not in st.session_state:
                st.session_state[audio_key] = generate_audio(row['Context'])
            st.audio(st.session_state[audio_key], format='audio/mp3', start_time=0)

if __name__ == "__main__":
    main()
