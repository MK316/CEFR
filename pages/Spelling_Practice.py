import streamlit as st
import pandas as pd
import numpy as np
from gtts import gTTS
from io import BytesIO
import random

# Assuming URLs to your text files hosted on GitHub
urls = {
    'Level B': 'https://raw.githubusercontent.com/yourusername/yourrepo/main/level_b.txt',
    'Level C': 'https://raw.githubusercontent.com/yourusername/yourrepo/main/level_c.txt'
}

def load_data(level):
    url = urls[level]
    data = pd.read_csv(url, sep='\t')  # Adjust delimiter based on your file format
    return data

def main():
    st.title("Word Practice App")
    
    # User inputs
    user_name = st.text_input("User name")
    level = st.radio("Select Level:", ['Level B', 'Level C'])
    data = load_data(level)
    
    sid_options = st.selectbox("Select SID:", data['SID'].unique())
    selected_data = data[data['SID'] == sid_options]
    
    order_type = st.radio("Choose order:", ['Sequential', 'Random'])
    if order_type == 'Random':
        selected_data = selected_data.sample(frac=1).reset_index(drop=True)
    
    start = st.button("Start")
    
    if start:
        for i, row in selected_data.iterrows():
            word = row['WORD']
            audio = gTTS(text=word, lang='en')
            audio_file = BytesIO()
            audio.save(audio_file)
            audio_file.seek(0)
            
            st.audio(audio_file)
            user_input = st.text_input("Type the word shown:", key=str(i))
            
            if user_input:
                correct = "Correct!" if user_input.lower() == word.lower() else "Incorrect"
                st.write(f"{word} - {correct}")
        
        st.button("Complete")

if __name__ == "__main__":
    main()
