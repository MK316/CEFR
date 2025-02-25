import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with caching
@st.cache_data
def load_data(file_url):
    df = pd.read_csv(file_url, sep='\t', usecols=['SID', 'WORD', 'POS'], dtype=str)  # Read all as strings

    # Strip any leading/trailing whitespace from column names
    df.columns = df.columns.str.strip()

    # Extract only the numeric part of SID
    df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)  # Extract numbers only and convert to integer

    # Extract only the first word from WORD column (in case extra info exists)
    df['WORD'] = df['WORD'].str.split().str[0]

    return df

def generate_audio(text):
    """Generate speech audio for a given text using gTTS."""
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()  # Return byte content

def main():
    st.markdown("### 🎧 Listen & Spell Practice")
    st.caption("Level B has 725 words and Level C has 1,380 words. These are additional 2K contained in the Oxford 5K vocabulary.")
    st.markdown("e.g., **'acid'** in _'Lemon juice is known for its high **acid** content._'")
    # Define tabs for different word lists
    tab1, tab2 = st.tabs(["💙 Level B", "💜 Level C"])

    with tab1:
        run_practice_app(
            user_name="User_LevelB",
            file_url="https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2.txt"
        )

    with tab2:
        run_practice_app(
            user_name="User_LevelC",
            file_url="https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1f.txt"
        )

def run_practice_app(user_name, file_url):
    data = load_data(file_url)  # Load the dataset
    total_words = len(data)  # Count available words

    user_name = st.text_input(f"Type user name ({user_name})")

    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input(f"Start SID (1~{total_words})", min_value=1, max_value=data['SID'].max(), value=1)
    with col2:
        end_sid = st.number_input(f"End SID (1~{total_words})", min_value=1, max_value=data['SID'].max(), value=min(start_sid + 19, data['SID'].max()))

    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)].reset_index(drop=True)

    audio_key_prefix = f"audio_{user_name}"
    input_key_prefix = f"input_{user_name}"

    if f'{audio_key_prefix}_data' not in st.session_state:
        st.session_state[f'{audio_key_prefix}_data'] = {}

    if f'{input_key_prefix}_inputs' not in st.session_state:
        st.session_state[f'{input_key_prefix}_inputs'] = {}

    if st.button(f'🔉 Generate Audio - {file_url[-6:-4]}'):
        st.session_state[f'{audio_key_prefix}_data'].clear()
        st.session_state[f'{input_key_prefix}_inputs'].clear()
        st.session_state[f'{audio_key_prefix}_generated'] = True  

        for row in filtered_data.itertuples():
            sid_key = f'{input_key_prefix}_{row.SID}_{file_url[-6:-4]}'  # Ensuring uniqueness
            st.session_state[f'{input_key_prefix}_inputs'][sid_key] = ""
            audio_key = f'{audio_key_prefix}_{row.SID}_{file_url[-6:-4]}'
            st.session_state[f'{audio_key_prefix}_data'][audio_key] = generate_audio(row.WORD)

    if st.session_state.get(f'{audio_key_prefix}_generated', False):
        for row in filtered_data.itertuples():
            audio_key = f'{audio_key_prefix}_{row.SID}_{file_url[-6:-4]}'
            sid_key = f'{input_key_prefix}_{row.SID}_{file_url[-6:-4]}'  # Uniqueness fix

            if audio_key in st.session_state[f'{audio_key_prefix}_data']:
                st.caption(f"SID {row.SID}")  
                st.audio(st.session_state[f'{audio_key_prefix}_data'][audio_key], format='audio/mp3')

                # Updated text input key to be unique
                st.text_input("Type the word shown:", key=sid_key, value="", placeholder="Type here...", label_visibility="collapsed")

    if st.button(f'🔑 Check Answers - {file_url[-6:-4]}'):
        correct_count = 0
        for row in filtered_data.itertuples():
            sid_key = f'{input_key_prefix}_{row.SID}_{file_url[-6:-4]}'  # Uniqueness fix
            user_input = st.session_state.get(sid_key, '').strip().lower()
            correct = user_input == row.WORD.lower()
            if correct:
                correct_count += 1
            st.write(f"Word: {row.WORD}, Your Input: {user_input}, Correct: {correct}")

        st.write(f"{user_name}: {correct_count}/{len(filtered_data)} correct.")


if __name__ == "__main__":
    main()
