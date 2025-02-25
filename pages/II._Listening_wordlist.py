import streamlit as st
import requests
import pandas as pd
import io
from gtts import gTTS
from pydub import AudioSegment
from io import BytesIO

# ✅ Load wordlist from GitHub
@st.cache_data
def load_wordlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error if request fails

        # Read as DataFrame
        df = pd.read_csv(io.StringIO(response.text), sep='\t', usecols=['SID', 'WORD'], dtype=str)

        # Clean and convert SID to integer
        df.columns = df.columns.str.strip()
        df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)
        df['WORD'] = df['WORD'].str.strip()  # Remove extra spaces

        return df
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame(columns=["SID", "WORD"])

# 🔹 Wordlist file URL (replace with your actual URL)
wordlist_url = "https://raw.githubusercontent.com/MK316/Engpro-Class/refs/heads/main/data/CEFRB1B2.txt"

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
    selected_words = wordlist[(wordlist['SID'] >= start_sid) & (wordlist['SID'] <= end_sid)]['WORD'].tolist()

    # ✅ Generate audio with 1-second silence between words
    def generate_audio(words):
        silence = AudioSegment.silent(duration=1000)  # 1-second silence
        combined_audio = AudioSegment.empty()

        for word in words:
            tts = gTTS(word, lang='en')
            word_audio = BytesIO()
            tts.write_to_fp(word_audio)
            word_audio.seek(0)

            # Convert gTTS output to AudioSegment
            segment = AudioSegment.from_file(word_audio, format="mp3")
            combined_audio += segment + silence  # Add silence after each word

        # Export final audio
        output_audio = BytesIO()
        combined_audio.export(output_audio, format="mp3")
        output_audio.seek(0)
        return output_audio

    # ✅ Button to generate and play audio
    if st.button("🎧 Generate Audio"):
        audio_file = generate_audio(selected_words)
        st.audio(audio_file, format="audio/mp3")

    # ✅ Display selected word list
    if selected_words:
        st.write("**Selected Words:**")
        st.write(", ".join(selected_words))
else:
    st.error("No data available in the wordlist.")
