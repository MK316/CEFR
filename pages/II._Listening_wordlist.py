import streamlit as st
import requests
import pandas as pd
import io
from gtts import gTTS
from io import BytesIO

# ✅ Load wordlist from GitHub
@st.cache_data
def load_wordlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error if request fails

        # Read as DataFrame
        df = pd.read_csv(io.StringIO(response.text), sep='\t', usecols=['SID', 'WORD', 'POS'], dtype=str)

        # Clean and convert SID to integer
        df.columns = df.columns.str.strip()
        df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)
        df['WORD'] = df['WORD'].str.strip()  # Remove extra spaces

        # ✅ Extract only the first word (removing POS)
        df['WORD'] = df['WORD'].apply(lambda x: x.split()[0])

        return df
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame(columns=["SID", "WORD"])

# 🔹 Wordlist file URL
wordlist_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2.txt"

# ✅ Streamlit App UI
st.title("🔊 Wordlist Audio Generator")

# Load wordlist
wordlist = load_wordlist(wordlist_url)

if not wordlist.empty:
    # User selects SID range
    col1, col2 = st.columns(2)
    with col1:
        start_sid = st.number_input("From SID", min_value=1, max_value=wordlist['SID'].max(), value=1)
    with col2:
        end_sid = st.number_input("To SID", min_value=start_sid, max_value=wordlist['SID'].max(), value=min(start_sid+19, wordlist['SID'].max()))

    # Filter selected words
    selected_data = wordlist[(wordlist['SID'] >= start_sid) & (wordlist['SID'] <= end_sid)][['SID', 'WORD']]

    # ✅ Generate audio including SID + WORD
    def generate_audio(data):
        combined_audio = BytesIO()

        for row in data.itertuples():
            text = f"Number {row.SID}, {row.WORD}"  # Example: "Number 1, specialize"
            tts = gTTS(text, lang='en')
            tts_audio = BytesIO()
            tts.write_to_fp(tts_audio)
            tts_audio.seek(0)

            combined_audio.write(tts_audio.read())  # Append word audio

        combined_audio.seek(0)
        return combined_audio

    # ✅ Button to generate and play audio
    if st.button("🎧 Generate Audio"):
        audio_file = generate_audio(selected_data)
        st.audio(audio_file, format="audio/mp3")

    # ✅ Display selected words with SID
    if not selected_data.empty:
        st.write("**Selected Words:**")
        st.dataframe(selected_data, hide_index=True)
else:
    st.error("No data available in the wordlist.")
