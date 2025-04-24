import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

st.set_page_config(page_title="EV Charging Station Insights", layout="wide")
st.title("EV Charging Station Insights (Google Maps Data)")

# API Key setup (use .env or Streamlit secrets)
OPENAI_API_KEY = st.secrets['OpenAI_API_KEY']
if not OPENAI_API_KEY:
    st.error("Please set your OPENAI_API_KEY in a .env file or Streamlit secrets.")
    st.stop()

# File loader
DATA_PATH = os.path.join(os.path.dirname(__file__), "cleaned_ev_data.csv")
if os.path.exists(DATA_PATH):
    EV_df = pd.read_csv(DATA_PATH)
    st.success(f"Loaded {DATA_PATH} successfully!")
else:
    st.error(f"Could not find {DATA_PATH}. Please ensure the file exists in the repository.")
    st.stop()

# Sidebar with predefined questions
st.sidebar.header("Predefined Analysis Questions")

predefined_questions = {
    "Location-Based Analysis": [
        "Which cities have the highest number of EV stations?",
        "List all vendors with station count in San Jose, CA, and show it in a bar chart.",
        "What is the average rank of stations in each city?",
    ],
    "Vendor Performance Insights": [
        "Which EV vendor has the most stations overall?",
        "Show average review score for each EV vendor in descending order.",
        "List all vendors and their total review count.",
    ],
    "Quality & Ranking": [
        "Which vendor has the best average rank across all locations?",
        "Which stations have the most user reviews? List top 5 with vendor and location.",
    ],
    "Trends & Strategy": [
        "Create a bar chart comparing total stations by vendor in California.",
    ],
}

category = st.sidebar.selectbox("Select Category", list(predefined_questions.keys()))
question = st.sidebar.radio(
    "Choose a question:",
    predefined_questions[category],
    key="predefined_question"
)

st.sidebar.markdown("---")
st.sidebar.markdown("Or type your own question below:")

user_prompt = st.text_area(
    "Ask a question about the EV charging station data:",
    value=question if question else "",
    key="main_prompt_box"
)

submit = st.button("Submit Query")

if submit and user_prompt:
    with st.spinner("Processing your query..."):
        query = user_prompt.lower()

        if "highest number of ev stations" in query:
            city_counts = EV_df['city'].value_counts().head(10)
            st.bar_chart(city_counts)

        elif "station count in san jose" in query:
            san_jose_df = EV_df[(EV_df['city'].str.lower() == "san jose") & (EV_df['state'].str.upper() == "CA")]
            vendor_counts = san_jose_df['EV Vendor'].value_counts()
            fig, ax = plt.subplots()
            sns.barplot(x=vendor_counts.values, y=vendor_counts.index, ax=ax)
            ax.set_title("EV Station Counts by Vendor in San Jose, CA")
            st.pyplot(fig)

        elif "average rank of stations in each city" in query:
            avg_rank = EV_df.groupby('city')['rank'].mean().sort_values()
            st.bar_chart(avg_rank.head(10))

        elif "most stations overall" in query:
            vendor_counts = EV_df['EV Vendor'].value_counts()
            st.bar_chart(vendor_counts.head(10))

        elif "average review score for each ev vendor" in query:
            avg_scores = EV_df.groupby('EV Vendor')['totalScore'].mean().sort_values(ascending=False)
            st.bar_chart(avg_scores.head(10))

        elif "total review count" in query:
            total_reviews = EV_df.groupby('EV Vendor')['reviewsCount'].sum().sort_values(ascending=False)
            st.bar_chart(total_reviews.head(10))

        elif "best average rank" in query:
            best_rank = EV_df.groupby('EV Vendor')['rank'].mean().sort_values()
            st.bar_chart(best_rank.head(10))

        elif "most user reviews" in query:
            top_reviews = EV_df[['EV Vendor', 'location', 'reviewsCount']].sort_values(by='reviewsCount', ascending=False).head(5)
            st.table(top_reviews)

        elif "total stations by vendor in california" in query:
            ca_df = EV_df[EV_df['state'].str.upper() == "CA"]
            ca_vendor_counts = ca_df['EV Vendor'].value_counts()
            fig, ax = plt.subplots()
            sns.barplot(x=ca_vendor_counts.values, y=ca_vendor_counts.index, ax=ax)
            ax.set_title("EV Stations by Vendor in California")
            st.pyplot(fig)

        else:
            st.warning("Query not recognized or not supported yet. Please rephrase or select a predefined option.")
