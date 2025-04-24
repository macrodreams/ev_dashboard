import streamlit as st
from transformers import pipeline

# Cache the model to avoid loading it repeatedly
@st.cache(allow_output_mutation=True)
def load_model():
    return pipeline("sentiment-analysis")

# Load the pre-trained sentiment analysis pipeline
sentiment_analyzer = load_model()

# Streamlit UI Elements
st.title("EV Charging Station Sentiment Analysis")
st.write("This app analyzes the sentiment of Google reviews for EV Charging Stations.")

# Input: User can type in or paste reviews
user_input = st.text_area("Enter a Review", "Type your review here...")

# Perform sentiment analysis when user submits input
if st.button("Analyze Sentiment"):
    if user_input:
        # Perform sentiment analysis
        result = sentiment_analyzer(user_input)
        sentiment_label = result[0]['label']
        sentiment_score = result[0]['score']

        # Display the sentiment result
        st.write(f"Sentiment: {sentiment_label}")
        st.write(f"Confidence Score: {sentiment_score:.2f}")
