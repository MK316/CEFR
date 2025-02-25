import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# Load data with caching
@st.cache
def load_data(file_url):
    df = pd.read_csv(file_url, sep='\t', usecols=['SID', 'WORD', 'POS', 'Context'], dtype=str)  # Read all columns including 'Context'
    df.columns = df.columns.str.strip()  # Strip any leading/trailing whitespace from column names
    df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)  # Extract numbers only and convert to integer
    df['WORD'] = df['WORD'].str.split().str[0]  # Extract only the first word from WORD column (in case extra info exists)
    return df

def generate_audio(text):
    """Generate speech audio for a given text using gTTS."""
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()  # Return byte content

def main():
    st.markdown("### 🎧 CEFR Listen & Spell Practice")
    st.caption("Level B has 725 words and Level C has 1,381 words. These are additional 2K contained in the Oxford 5K vocabulary.")

    # Define tabs for different word lists
    tab1, tab2 = st.tabs(["Level B", "Level C"])

    with tab1:
        run_practice_app(
            user_name="User_LevelB",
            file_url="https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2WICf.csv"
        )

    with tab2:
        run_practice_app(
            user_name="User_LevelC",
            file_url="https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1WIC.txt"
        )

def run_practice_app(user_name, file_url):
    data = load_data(file_url)  # Load the dataset
    total_words = len(data)  # Count available words

    user_name = st.text_input(f"Type user name ({user_name})")
    
    # Layout adjustment: Put Start SID and End SID in one row
    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input(f"Start SID (1~{total_words})", min_value=1, max_value=total_words, value=1)
    with col2:
        end_sid = st.number_input(f"End SID (1~{total_words})", min_value=1, max_value=total_words, value=min(start_sid + 19, total_words))

    # Filter words based on selected SID range
    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)].reset_index(drop=True)

    # Unique session state keys per tab
    audio_key_prefix = f"audio_{user_name}"
    input_key_prefix = f"input_{user_name}"

    if st.button(f'🔉 Generate Audio - {file_url[-6:-4]}'):  # Unique button per file
        # Reset session state on new generation
        st.session_state[audio_key_prefix] = {f'{audio_key_prefix}_{row.SID}': generate_audio(row.Context) for row in filtered_data.itertuples()}
        st.session_state[f'{audio_key_prefix}_generated'] = True  

    if st.session_state.get(f'{audio_key_prefix}_generated', False):
        for row in filtered_data.itertuples():
            audio_key = f'{audio_key_prefix}_{row.SID}'
            st.caption(f"SID {row.SID} - {row.WORD}")
            st.audio(st.session_state[audio_key], format='audio/mp3')

if __name__ == "__main__":
    main()
