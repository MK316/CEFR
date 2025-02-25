import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd
import hashlib

@st.cache_data
def load_data(file_url):
    # Determine the separator based on file extension
    if file_url.endswith('.txt'):
        sep = '\t'  # Tab-separated for .txt files
    elif file_url.endswith('.csv'):
        sep = ','   # Comma-separated for .csv files
    else:
        raise ValueError("Unsupported file format. Please use .txt or .csv files.")

    # Load the data with the determined separator
    try:
        df = pd.read_csv(file_url, sep=sep)
        df.columns = [col.strip() for col in df.columns]  # Ensure columns are trimmed of whitespace

        # Verify all required columns are present
        expected_columns = {'SID', 'WORD', 'POS', 'Context'}
        if not expected_columns.issubset(df.columns):
            missing_cols = expected_columns - set(df.columns)
            raise ValueError(f"Missing columns in the data file: {', '.join(missing_cols)}")

        # Convert SID to integer if possible
        df['SID'] = df['SID'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        raise

def generate_audio(text):
    """Generate speech audio for a given text using gTTS."""
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()  # Return byte content

def create_unique_key(base_key, user_name, file_url, identifier):
    # Create a unique hash of the file URL
    hash_object = hashlib.sha256(file_url.encode() + str(identifier).encode())
    unique_suffix = hash_object.hexdigest()[:8]  # Use only the first 8 characters for brevity
    return f"{base_key}_{user_name}_{unique_suffix}"

def main():
    st.markdown("### 🎧 CEFR Listen & Spell Practice")
    st.caption("Level B has 725 words and Level C has 1,381 words. These are additional 2K contained in the Oxford 5K vocabulary.")

    # Define tabs for different word lists
    tab1, tab2 = st.tabs(["Level B", "Level C"])

    # Use session-specific identifiers to differentiate instances
    session_id = st.session_state.get('session_id', 0)

    with tab1:
        run_practice_app(
            user_name="User_LevelB",
            file_url="https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2WICf.csv",
            session_id=session_id
        )

    with tab2:
        run_practice_app(
            user_name="User_LevelC",
            file_url="https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1WICf.csv",
            session_id=session_id
        )

    # Increment session id on each run to ensure new keys
    st.session_state['session_id'] = session_id + 1

def run_practice_app(user_name, file_url, session_id):
    data = load_data(file_url)  # Load the dataset
    total_words = len(data)  # Count available words

    user_name_input = st.text_input(f"Type user name ({user_name})", key=f"user_name_{user_name}")

    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input(f"Start SID (1~{total_words})", min_value=1, max_value=total_words, value=1, key=f"start_sid_{user_name}")
    with col2:
        end_sid = st.number_input(f"End SID (1~{total_words})", min_value=1, max_value=total_words, value=min(start_sid + 19, total_words), key=f"end_sid_{user_name}")

    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)].reset_index(drop=True)
    button_key = create_unique_key('generate_audio', user_name_input, file_url, session_id)

    if st.button(f'🔉 Generate Audio - {file_url[-6:-4]}', key=button_key):
        # Generate audio and store in session state
        for row in filtered_data.itertuples():
            audio_key = create_unique_key('audio', str(row.SID), file_url, session_id)
            st.session_state[audio_key] = generate_audio(row.Context)

    if 'audio_generated' not in st.session_state:
        st.session_state['audio_generated'] = {}

    for row in filtered_data.itertuples():
        audio_key = create_unique_key('audio', str(row.SID), file_url, session_id)
        if audio_key in st.session_state:
            st.caption(f"SID {row.SID} - {row.WORD}")
            st.audio(st.session_state[audio_key], format='audio/mp3')

if __name__ == "__main__":
    main()
