import streamlit as st
import requests
import pandas as pd
import io  # ✅ Corrected StringIO import

# URLs for wordlists
wordlist_urls = {
    "🍐 Wordlist B1B2": "https://raw.githubusercontent.com/MK316/Engpro-Class/refs/heads/main/data/CEFRB1B2.txt",
    "🍓 Wordlist C1": "https://raw.githubusercontent.com/MK316/Engpro-Class/refs/heads/main/data/CEFRC1.txt"
}

# Function to load wordlist data
@st.cache_data
def load_wordlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for invalid requests

        # ✅ Fixed: Using io.StringIO instead of pd.compat.StringIO
        df = pd.read_csv(io.StringIO(response.text), sep='\t', usecols=['SID', 'WORD'], dtype=str)

        # Strip whitespace and convert SID to integer
        df.columns = df.columns.str.strip()
        df['SID'] = df['SID'].str.extract('(\d+)')[0].astype(int)  # Extract numbers and convert
        df['WORD'] = df['WORD'].str.strip()  # Clean up words
        return df
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame(columns=["SID", "WORD"])  # Return empty DataFrame on error

# Create tabs for different wordlists
tabs = st.tabs(list(wordlist_urls.keys()))

# Loop through tabs dynamically
for idx, (tab_name, url) in enumerate(wordlist_urls.items()):
    with tabs[idx]:  # Assign content to each tab
        st.caption("📅 Spring 2025")

        # Load wordlist
        wordlist = load_wordlist(url)

        if not wordlist.empty:
            # Show total words available
            total_words = len(wordlist)
            st.info(f"📌 This wordlist contains **{total_words} words**.")

            # User selects SID range
            col1, col2 = st.columns(2)
            with col1:
                start_sid = st.number_input("From SID", min_value=1, max_value=wordlist['SID'].max(), value=1)
            with col2:
                end_sid = st.number_input("To SID", min_value=start_sid, max_value=wordlist['SID'].max(), value=min(start_sid+19, wordlist['SID'].max()))

            # Filter and display selected range
            filtered_words = wordlist[(wordlist['SID'] >= start_sid) & (wordlist['SID'] <= end_sid)]

            # Display words in table format
            st.dataframe(filtered_words, use_container_width=True, index=False)

        else:
            st.error("No data available for this wordlist.")
