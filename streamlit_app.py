import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Add theme toggle
theme = st.radio("Select Theme", ["Light", "Dark"])

if theme == "Dark":
    st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
    }
    .sidebar {
        background-color: #2e2e2e;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body {
        background-color: white;
        color: black;
    }
    .sidebar {
        background-color: #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="EV Charging Station Insights", layout="wide")
st.title("EV Charging Station Insights (Google Maps Data)")

# API Key setup (use .env or Streamlit secrets)
OPENAI_API_KEY = st.secrets['OpenAI_API_KEY']
if not OPENAI_API_KEY:
    st.error("Please set your OPENAI_API_KEY in a .env file or Streamlit secrets.")
    st.stop()

# File loader: load from repo instead of upload
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
    "Risk/Complaint Indicators": [
        "Summarize common user complaints based on reviews.",
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

# Main UI prompt box (pre-filled with selected question)
user_prompt = st.text_area(
    "Ask a question about the EV charging station data:",
    value=question if question else "",
    key="main_prompt_box"
)

if st.button("Submit Query") and user_prompt:
    with st.spinner("Processing your query..."):
        refined = refine_prompt(user_prompt)
        st.info(f"Refined User Question: {refined}")  # Display the refined prompt in the Streamlit UI
        response = EV_SmartDF.chat(refined)
        final_response = clean_llm_output(response)
    st.subheader("LLM Response:")
    st.write(final_response)
    # Try to display chart if present
    if hasattr(response, 'chart') and response.chart is not None:
        try:
            import matplotlib.figure
            if isinstance(response.chart, matplotlib.figure.Figure):
                st.pyplot(response.chart)
            elif isinstance(response.chart, str) and (response.chart.endswith('.png') or response.chart.endswith('.jpg')):
                from PIL import Image
                import os
                if os.path.exists(response.chart):
                    img = Image.open(response.chart)
                    st.image(img, caption="Generated Chart")
                else:
                    st.warning(f"Chart image file not found: {response.chart}")
        except Exception as e:
            st.warning(f"Could not display chart: {e}")
