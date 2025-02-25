import streamlit as st

st.markdown("""
  ### ❄️ Vocabulary practice application hub
  This page introduces and provides guidance on using an app designed to help college freshmen and sophomores learn vocabulary with audio support. The vocabulary focuses on 2,000 additional words from the Oxford Learner’s Dictionary 3K, which have been incorporated to enhance learning. These additional 2K words correspond to CEFR B2 and C1 levels, supporting learners in expanding their academic and professional English skills.
  """)        

# GitHub raw image URL
image_url = "https://github.com/MK316/CEFR/raw/main/data/learnwithsound.png"

# Display image with specified width
st.image(image_url, width=300)
st.caption("Last updated: Feb. 25, 2025")
