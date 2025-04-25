import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
import requests

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

# Google Maps API functions for fetching reviews and ratings
API_KEY = st.secrets['GOOGLE_API_KEY']

def get_place_id(name, lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": API_KEY,
        "location": f"{lat},{lng}",
        "radius": 100,
        "keyword": name
    }
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    if results:
        return results[0]["place_id"]
    return None

def get_reviews(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "key": API_KEY,
        "place_id": place_id,
        "fields": "rating,reviews"
    }
    response = requests.get(url, params=params)
    return response.json().get("result", {})

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
        "Which vendors have presence across the most number of cities?",
    ],
    "Quality & Ranking": [
        "Which vendor has the best average rank across all locations?",
        "Which stations have the most user reviews? List top 5 with vendor and location.",
    ],
    "Trends & Strategy": [
        "Create a bar chart comparing total stations by vendor in California.",
        "What trends are emerging in vendor performance across major metro areas?",
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

custom_question = st.sidebar.text_area(
    "Ask a custom question about the EV charging station data:",
    placeholder="e.g., Show station counts by vendor in Los Angeles, CA",
    key="main_prompt_box"
)

# Choose which query to send — user typed one, or predefined
final_prompt = custom_question.strip() if custom_question.strip() else question

submit = st.sidebar.button("Submit Query")

if submit and final_prompt:
    with st.spinner("Processing your query..."):
        query = final_prompt.lower()

        if "highest number of ev stations" in query:
            city_counts = EV_df['city'].value_counts().head(10)
            st.bar_chart(city_counts)

        elif "station count in san jose" in query:
            # Filter for stations in San Jose, CA
            san_jose_df = EV_df[(EV_df['city'].str.lower() == "san jose") & (EV_df['state'].str.upper() == "CA")]
            
            # Count the number of stations for each vendor in San Jose
            vendor_counts = san_jose_df['EV Vendor'].value_counts()
            
            # Create the bar chart to display the station count per vendor
            fig, ax = plt.subplots()
            sns.barplot(x=vendor_counts.values, y=vendor_counts.index, ax=ax)
            ax.set_title("EV Station Counts by Vendor in San Jose, CA")
            ax.set_xlabel("Station Count")
            ax.set_ylabel("Vendor")
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
            # Calculate the average rank for each vendor
            avg_rank = EV_df.groupby('EV Vendor')['rank'].mean().sort_values()

            # Display the vendor with the best (lowest) average rank
            best_vendor = avg_rank.head(1)
            st.write(f"Vendor with the Best Average Rank Across All Locations:")
            st.write(f"{best_vendor.index[0]} with an average rank of {best_vendor.values[0]:.2f}")

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

        # Trend analysis for vendor performance across metro areas
        elif "trends are emerging in vendor performance" in query or "what trends are emerging in vendor performance" in query:
            # Trend in number of stations per vendor across major metro areas
            vendor_station_trends = EV_df.groupby(['city', 'EV Vendor']).size().unstack(fill_value=0)
            st.write("Trend in Station Counts per Vendor Across Major Metro Areas")
            st.line_chart(vendor_station_trends)

            # Trend in average review scores per vendor across major metro areas
            vendor_review_trends = EV_df.groupby(['city', 'EV Vendor'])['totalScore'].mean().unstack(fill_value=0)
            st.write("Trend in Average Review Scores per Vendor Across Major Metro Areas")
            st.line_chart(vendor_review_trends)

            # Rank trends across vendors in major cities
            vendor_rank_trends = EV_df.groupby(['city', 'EV Vendor'])['rank'].mean().unstack(fill_value=0)
            st.write("Trend in Vendor Rankings Across Major Metro Areas")
            st.line_chart(vendor_rank_trends)

            # Identify vendors expanding across multiple metro areas
            city_vendor_counts = EV_df.groupby(['EV Vendor', 'city']).size().unstack(fill_value=0)
            top_expanding_vendors = city_vendor_counts.sum(axis=1).sort_values(ascending=False).head(5)
            st.write("Top 5 Vendors Expanding Across the Most Metro Areas")
            st.bar_chart(top_expanding_vendors)

        # New logic for vendors with presence across the most number of cities
        elif "which vendors have presence across the most number of cities" in query:
            # Count the number of unique cities each vendor operates in
            vendor_city_count = EV_df.groupby('EV Vendor')['city'].nunique().sort_values(ascending=False)
            
            # Display the top vendors with the most presence across cities
            st.write("Vendors with Presence Across the Most Number of Cities:")
            st.table(vendor_city_count.head(10))

        # New logic for retrieving and displaying Google Maps reviews and ratings
        elif "reviews" in query or "rating" in query:
            # Fetch Place ID based on a specific location
            name = "ChargePoint Charging Station"  # Modify as needed
            lat = 37.339623  # Modify with relevant latitude
            lng = -121.896821  # Modify with relevant longitude
            
            place_id = get_place_id(name, lat, lng)

            if place_id:
                details = get_reviews(place_id)
                st.subheader("⭐ Rating:")
                st.write(details.get("rating", "No rating available"))
                st.subheader("🗣️ Sample Review:")
                review_text = details.get("reviews", [{}])[0].get("text", "No reviews available")
                st.write(review_text)
            else:
                st.error("Could not find reviews for the specified station.")
        else:
            st.warning("Query not recognized or not supported yet. Please rephrase or select a predefined option.")
