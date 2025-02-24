import streamlit as st
import requests
import pandas as pd
import io

# URLs for wordlists
wordlist_urls = {
    "🍐 Wordlist B2": "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/B2.txt",
    "🍓 Wordlist C1": "https://raw.githubusercontent.com/MK316/CEFR/refs/heads/main/data/C1.txt"
}

# Function to load wordlist data
@st.cache_data
def load_wordlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for invalid requests

        # ✅ Load all three columns: SID, WORD, and POS
        df = pd.read_csv(io.StringIO(response.text), sep='\t', dtype=str)

        # Strip whitespace and convert SID to integer
        df.columns = df.columns.str.strip()  # Strip any leading/trailing spaces from column names
        df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)  # Extract numbers and convert
        df['WORD'] = df['WORD'].str.strip()  # Clean up words
        df['POS'] = df['POS'].str.strip()  # Clean up POS

        return df
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame(columns=["SID", "WORD", "POS"])  # Return empty DataFrame on error

# Create tabs for different wordlists
tabs = st.tabs(list(wordlist_urls.keys()))

# Loop through tabs dynamically
for idx, (tab_name, url) in enumerate(wordlist_urls.items()):
    with tabs[idx]:  # Assign content to each tab
        st.caption("🔎 The B2 and C1 word lists contain a total of 725 and 1,381 words, respectively. Select the word numbers you want, then click the Show button.")
        st.markdown("---")
        
        # Load wordlist
        wordlist = load_wordlist(url)

        if not wordlist.empty:
            total_words = len(wordlist)  # Get total words in the wordlist
            
            # User selects SID range
            col1, col2 = st.columns(2)
            with col1:
                start_sid = st.number_input(f"From SID (Total: {total_words} words)", min_value=1, max_value=wordlist['SID'].max(), value=1)
            with col2:
                end_sid = st.number_input(f"To SID (Total: {total_words} words)", min_value=start_sid, max_value=wordlist['SID'].max(), value=min(start_sid+19, wordlist['SID'].max()))

            # Filter selected range
            filtered_words = wordlist[(wordlist['SID'] >= start_sid) & (wordlist['SID'] <= end_sid)].reset_index(drop=True)

            # ✅ "Show Words" Button with number of selected words
            num_selected = len(filtered_words)
            if st.button(f"🔍 Show {num_selected} Words", key=f"show_words_{idx}"):
                st.table(filtered_words.set_index("SID"))

        else:
            st.error("No data available for this wordlist.")
