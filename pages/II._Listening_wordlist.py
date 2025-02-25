import streamlit as st
import requests
import pandas as pd
import io
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment

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
    selected_words = wordlist[(wordlist['SID'] >= start_sid) & (wordlist['SID'] <= end_sid)]['WORD'].tolist()

    # ✅ Generate audio with 1-second silence between words (Using pydub for merging)
    def generate_audio(words):
        combined_audio = AudioSegment.empty()

        # ✅ Load pre-generated 1-second silent MP3
        silent_mp3_url = "https://github.com/MK316/CEFR/raw/main/data/silence.mp3"
        silent_response = requests.get(silent_mp3_url)
        silent_audio = AudioSegment.from_file(BytesIO(silent_response.content), format="mp3")

        for word in words:
            # Generate TTS audio
            tts = gTTS(word, lang='en')
            tts_audio = BytesIO()
            tts.write_to_fp(tts_audio)
            tts_audio.seek(0)

            # Convert gTTS output to AudioSegment
            word_audio = AudioSegment.from_file(tts_audio, format="mp3")

            # ✅ Append word audio + silence
            combined_audio += word_audio + silent_audio

        # ✅ Export final audio
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
