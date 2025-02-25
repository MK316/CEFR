import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with caching
@st.experimental_memo
def load_data(file_url):
    df = pd.read_csv(file_url, sep='\t', usecols=['SID', 'WORD', 'POS'], dtype=str)
    df.columns = df.columns.str.strip()
    df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)
    df['WORD'] = df['WORD'].str.split().str[0]
    return df

def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()

def main():
    st.markdown("### 🎧 CEFR Listen & Spell Practice")
    st.caption("Level B has 725 words and Level C has 1,380 words. These are additional 2K contained in the Oxford 5K vocabulary.")

    tab1, tab2 = st.tabs(["Level B", "Level C"])

    with tab1:
        run_practice_app("User_LevelB", "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2.txt")

    with tab2:
        run_practice_app("User_LevelC", "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1.txt")

def run_practice_app(user_name, file_url):
    data = load_data(file_url)
    total_words = len(data)

    st.info(f"This level contains {total_words} words. Choose your SID range below.")

    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input(f"Start SID (1~{total_words})", min_value=1, max_value=data['SID'].max(), value=1)
    with col2:
        end_sid = st.number_input(f"End SID (1~{total_words})", min_value=1, max_value=data['SID'].max(), value=min(start_sid + 19, data['SID'].max()))

    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)]

    if st.button(f'🔉 Generate Audio - {file_url[-6:-4]}'):
        for row in filtered_data.itertuples():
            audio_key = f"{user_name}_audio_{row.SID}"
            st.session_state[audio_key] = generate_audio(row.WORD)
            st.caption(f"SID {row.SID} - {row.WORD}")
            st.audio(st.session_state[audio_key], format='audio/mp3')

    if st.button(f'🔑 Check Answers - {file_url[-6:-4]}'):
        correct_count = 0
        for row in filtered_data.itertuples():
            sid_key = f"{user_name}_input_{row.SID}"
            user_input = st.session_state.get(sid_key, '').strip().lower()
            correct = user_input == row.WORD.lower()
            st.write(f"Word: {row.WORD}, Your Input: {user_input}, Correct: {correct}")
            if correct:
                correct_count += 1
        st.write(f"{user_name}: {correct_count}/{len(filtered_data)} correct.")

if __name__ == "__main__":
    main()
