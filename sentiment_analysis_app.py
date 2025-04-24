import streamlit as st
from transformers import pipeline
import matplotlib.pyplot as plt

# Load the pre-trained sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

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

        # Optional: Show a bar chart to visualize sentiment
        fig, ax = plt.subplots()
        ax.bar(sentiment_label, sentiment_score, color='skyblue')
        ax.set_xlabel('Sentiment')
        ax.set_ylabel('Confidence Score')
        st.pyplot(fig)

    else:
        st.write("Please enter a review to analyze!")
