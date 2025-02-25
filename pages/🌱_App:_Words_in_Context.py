import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

@st.cache_data
def load_data(file_url):
    # Determine the separator based on file extension
    sep = ',' if file_url.endswith('.csv') else '\t'
    df = pd.read_csv(file_url, sep=sep)
    df.columns = [col.strip() for col in df.columns]  # Ensure columns are trimmed of whitespace
    df['SID'] = df['SID'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    return df

def generate_audio(text):
    """Generate speech audio for a given text using gTTS."""
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
    if data is None or data.empty:
        st.error("Failed to load data or data is empty.")
        return

    st.subheader(f"Generate Audio for {level}")
    # User can input the exact numbers for SID start and end
    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input('Start SID', min_value=int(data['SID'].min()), max_value=int(data['SID'].max()), value=int(data['SID'].min()))
    with col2:
        end_sid = st.number_input('End SID', min_value=int(data['SID'].min()), max_value=int(data['SID'].max()), value=int(data['SID'].min()) + 20)

    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)]

    if st.button(f'Generate Audio for {level}'):
        for index, row in filtered_data.iterrows():
            audio_key = f"audio_{level}_{row['SID']}"
            if audio_key not in st.session_state:
                st.session_state[audio_key] = generate_audio(row['Context'])
            st.caption(f"SID {row['SID']} - {row['WORD']}")
            st.audio(st.session_state[audio_key], format='audio/mp3', start_time=0)

if __name__ == "__main__":
    main()
