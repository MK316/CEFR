import streamlit as st
from gtts import gTTS
from io import BytesIO
import pandas as pd

# URLs to your text files hosted on GitHub
urls = {
    'Level B': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRB1B2.txt',
    'Level C': 'https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/CEFRC1.txt'
}

def load_data(level):
    # Load data assuming that the file uses tabs as delimiters and has a header row
    data = pd.read_csv(urls[level], sep='\t', usecols=['SID', 'WORD'])  # only load the SID and WORD columns
    return data

def main():
    st.title("Word Practice App")
    
    user_name = st.text_input("User name")
    level = st.radio("Select Level:", list(urls.keys()))
    data = load_data(level)

    # Generate SID ranges based on the data
    max_sid = data['SID'].max()
    sid_ranges = [(i, min(i+19, max_sid)) for i in range(1, max_sid, 20)]
    selected_range = st.selectbox("Select SID Range:", sid_ranges, format_func=lambda x: f"{x[0]}-{x[1]}")
    selected_data = data[(data['SID'] >= selected_range[0]) & (data['SID'] <= selected_range[1])]

    order_type = st.radio("Choose Order:", ['Sequential', 'Random'])
    if order_type == 'Random':
        selected_data = selected_data.sample(frac=1).reset_index(drop=True)

    if st.button("Start"):
        for _, row in selected_data.iterrows():
            word = row['WORD'].strip()  # strip any whitespace
            tts = gTTS(text=word, lang='en')
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            st.audio(audio_file, format='audio/mp3')
            user_input = st.text_input("Type the word shown:", key=row['SID'])
            if user_input:
                correct = "Correct" if user_input.strip().lower() == word.lower() else "Incorrect"
                st.write(f"{word} - {correct}")

    if st.button("Complete"):
        st.write(f"{user_name}: Score goes here")  # Implement scoring logic

if __name__ == "__main__":
    main()
