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
    st.markdown("### 🎧 Words in Context (WIC) practice")
    st.caption("Improve your vocabulary comprehension and pronunciation skills by listening to words used in context across various levels. Level B (1-725), Level C(1-1380)")
    st.markdown("e.g., **'acid'** in _'Lemon juice is known for its high **acid** content._'")
    tab1, tab2 = st.tabs(["💙 Level B", "💜 Level C"])

    with tab1:
        data_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2WICf.csv"
        run_practice_app("Level B", data_url)

    with tab2:
        data_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1WICff.csv"
        run_practice_app("Level C", data_url)

def run_practice_app(level, file_url):
    data = load_data(file_url)
    if data is None or data.empty:
        st.error("Failed to load data or data is empty.")
        return

    st.subheader(f"Practice with sound: {level}")
    total_sids = len(data)  # Calculate the total number of SIDs available

    # User can input the exact numbers for SID start and end
    col1, col2 = st.columns(2)
    # Ensure the min SID is at least 1
    min_sid = max(int(data['SID'].min()), 1) if not data.empty else 1
    max_sid = int(data['SID'].max()) if not data.empty else 1
    default_start_sid = min_sid
    default_end_sid = min(min_sid + 20, max_sid)

    with col1:
        start_sid = st.number_input('Start SID', min_value=min_sid, max_value=max_sid, value=default_start_sid, help=f"Choose a starting SID from 1 to {total_sids}")
    with col2:
        end_sid = st.number_input(f'End SID (total words: {total_sids})', min_value=min_sid, max_value=max_sid, value=default_end_sid, help=f"Choose an ending SID from 1 to {total_sids}")

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
