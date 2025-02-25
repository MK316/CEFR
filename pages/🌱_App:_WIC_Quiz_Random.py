import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd
import re
import random

@st.cache_data
def load_data(file_url):
    sep = ',' if file_url.endswith('.csv') else '\t'
    df = pd.read_csv(file_url, sep=sep)
    df.columns = [col.strip() for col in df.columns]  
    df['SID'] = df['SID'].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    return df

def generate_audio(text):
    """Generate speech audio for a given text using gTTS."""
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file.getvalue()

def mask_word(sentence, target_word):
    """Replace the target word in the sentence with '_______'."""
    return re.sub(rf'\b{re.escape(target_word)}\b', '_______', sentence, flags=re.IGNORECASE)

def main():
    st.markdown("### 🎧 Words in Context (WIC) Quiz")
    st.caption("Listen to the sentence and identify the missing word. Type the correct word in the blank and check your answers!")

    st.markdown("e.g., **'acid'** after listening to the audio saying _'Lemon juice is known for its high _______ content._'")

    user_id = st.text_input("👤 Enter your User ID", key="user_id")

    if user_id:
        tab1, tab2 = st.tabs(["💙 Level B", "💜 Level C"])

        with tab1:
            data_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2WICf.csv"
            run_practice_app("Level B", data_url, user_id)

        with tab2:
            data_url = "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1WICff.csv"
            run_practice_app("Level C", data_url, user_id)

def run_practice_app(level, file_url, user_id):
    data = load_data(file_url)
    if data.empty:
        st.error("Failed to load data or data is empty.")
        return

    st.subheader(f"Practice with Sound: {level}")
    total_sids = len(data)

    # SID Selection
    col1, col2, col3 = st.columns(3)
    min_sid = max(int(data['SID'].min()), 1)
    max_sid = int(data['SID'].max())

    with col1:
        start_sid = st.number_input("Start SID", min_value=min_sid, max_value=max_sid, value=min_sid)
    with col2:
        end_sid = st.number_input("End SID", min_value=min_sid, max_value=max_sid, value=min(start_sid + 19, max_sid))
    with col3:
        num_words = st.number_input("Number of words", min_value=1, max_value=20, value=10, help="Select how many words to practice.")

    filtered_data = data[(data['SID'] >= start_sid) & (data['SID'] <= end_sid)]

    # Ensure session state for generated words
    if f"{user_id}_{level}_generated_items" not in st.session_state:
        st.session_state[f"{user_id}_{level}_generated_items"] = {}

    if f"{user_id}_{level}_user_inputs" not in st.session_state:
        st.session_state[f"{user_id}_{level}_user_inputs"] = {}

    # **Button to generate quiz**
    if st.button(f'🔉 Generate Quiz for {level}'):
        # Select random words based on user input
        selected_words = random.sample(filtered_data.to_dict(orient="records"), min(num_words, len(filtered_data)))
        st.session_state[f"{user_id}_{level}_generated_items"] = {}

        for row in selected_words:
            sid_key = f"{user_id}_{level}_input_{row['SID']}"
            audio_key = f"{user_id}_audio_{level}_{row['SID']}"

            if sid_key not in st.session_state[f"{user_id}_{level}_generated_items"]:
                masked_sentence = mask_word(row['Context'], row['WORD'])

                st.session_state[f"{user_id}_{level}_generated_items"][sid_key] = {
                    "audio": generate_audio(row['Context']),
                    "masked_sentence": masked_sentence,
                    "correct_word": row['WORD']
                }

            # Ensure user input persists
            if sid_key not in st.session_state[f"{user_id}_{level}_user_inputs"]:
                st.session_state[f"{user_id}_{level}_user_inputs"][sid_key] = ""

    # **Display Questions Only After Generating Quiz**
    if f"{user_id}_{level}_generated_items" in st.session_state and st.session_state[f"{user_id}_{level}_generated_items"]:
        for sid_key, item in st.session_state[f"{user_id}_{level}_generated_items"].items():
            st.caption(f"{item['masked_sentence']}")
            st.audio(item["audio"], format='audio/mp3')

            # Persistent text input
            st.session_state[f"{user_id}_{level}_user_inputs"][sid_key] = st.text_input(
                "Type the missing word:", 
                key=sid_key, 
                value=st.session_state[f"{user_id}_{level}_user_inputs"][sid_key], 
                placeholder="Type here..."
            )

    # **Check Answers Button**
    if st.button(f'🔑 Check Answers - {level}'):
        correct_count = 0
        incorrect_sentences = []

        for sid_key, item in st.session_state[f"{user_id}_{level}_generated_items"].items():
            user_input = st.session_state[f"{user_id}_{level}_user_inputs"].get(sid_key, "").strip().lower()
            correct_word = item["correct_word"].lower()

            if user_input == correct_word:
                correct_count += 1
            else:
                incorrect_sentences.append(f"{item['masked_sentence']}")

        # Display results
        st.write(f"✅ Correct: {correct_count} / {len(st.session_state[f'{user_id}_{level}_generated_items'])}")

        if incorrect_sentences:
            st.markdown("### ❌ Incorrect Sentences (Try Again)")
            for sentence in incorrect_sentences:
                st.write(sentence)

if __name__ == "__main__":
    main()
