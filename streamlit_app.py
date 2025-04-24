import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import openai
import matplotlib
from PIL import Image

# Load environment variables
load_dotenv()

st.set_page_config(page_title="EV Charging Station Insights", layout="wide")
st.title("EV Charging Station Insights (Google Maps Data)")

# API Key setup (use .env or Streamlit secrets)
OPENAI_API_KEY = st.secrets['OpenAI_API_KEY']
if not OPENAI_API_KEY:
    st.error("Please set your OPENAI_API_KEY in a .env file or Streamlit secrets.")
    st.stop()
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# File loader: load from repo instead of upload
DATA_PATH = os.path.join(os.path.dirname(__file__), "cleaned_ev_data.csv")
if os.path.exists(DATA_PATH):
    EV_df = pd.read_csv(DATA_PATH)
    st.success(f"Loaded {DATA_PATH} successfully!")
else:
    st.error(f"Could not find {DATA_PATH}. Please ensure the file exists in the repository.")
    st.stop()

system_prompt = """
You are a data assistant for an electric vehicle (EV) charging station dashboard.

You must ONLY access and query the columns required to answer the user's question. Do NOT scan or consider the full dataset unless absolutely necessary.

Available columns include:
- EV Vendor
- city
- state
- address
- totalScore
- reviewsCount
- categoryName
- rank
- location

Ignore any large or nested fields like: reviews, reviewsDistribution, popularTimesHistogram, or detailed JSONs unless specifically asked.

Avoid including the full DataFrame or long context in your output. Respond clearly, concisely, and use only what’s needed.

Charts or tables must reference filtered data, not full dumps.

Your job is to reduce token usage while delivering actionable insights.
"""

llm = OpenAI(Model="GPT-4o")
EV_SmartDF = SmartDataframe(EV_df, config={"llm": llm, "system_message": system_prompt})

def refine_prompt(user_prompt):
    client = OpenAI()
    system_instruction = """
You are a data analyst assistant helping refine user questions for a SmartDataframe
containing EV charging station data from Google Maps.

Make the prompt specific, concise, and compatible with PandasAI.
Avoid using advanced or restricted matplotlib methods like 'tight_layout' or 'gca'.
Prefer simple operations like group by, counts, averages, bar/line plots.
Use field names like: EV Vendor, city, state, rank, totalScore, reviewsCount, etc.
Format the prompt clearly and naturally for LLM data querying.
Return only the improved prompt. Do NOT explain or comment.
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def clean_llm_output(raw_output):
    client = OpenAI()
    system_instruction = """
You are a cleanup assistant for an AI data chatbot.

You are given raw LLM output which might include logs, errors, tracebacks, retries, or system warnings.
Your job is to extract and return only the clean, relevant answer for the user.

If a chart or table is included, describe it briefly or return it cleanly.
Ignore any lines like:
- ERROR:...
- WARNING:...
- Traceback...
- Retry number...
- ModuleNotFoundError...
- Any internal PandasAI or matplotlib error logs

Do not explain what you did — just return the clean result.
"""
    safe_output = str(raw_output)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": safe_output}
        ]
    )
    return response.choices[0].message.content.strip()

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
        try:
            response = EV_SmartDF.chat(refined)
            st.write(f"Raw Response from LLM: {response}")  # Debugging: Log the raw response
            final_response = clean_llm_output(response)
        except Exception as e:
            st.error(f"Error occurred during query execution: {e}")
            final_response = None

    if final_response:
        st.subheader("LLM Response:")
        st.write(final_response)
        
        # Check if the response contains a chart (like a PNG or JPG file)
        if hasattr(response, 'chart') and response.chart:
            try:
                import matplotlib.figure
                if isinstance(response.chart, matplotlib.figure.Figure):
                    # Display the figure directly if it's a Matplotlib object
                    st.pyplot(response.chart)
                elif isinstance(response.chart, str) and (response.chart.endswith('.png') or response.chart.endswith('.jpg')):
                    from PIL import Image
                    import os
                    # Check if the chart file exists and render it
                    if os.path.exists(response.chart):
                        img = Image.open(response.chart)
                        st.image(img, caption="Generated Chart")
                    else:
                        st.warning(f"Chart image file not found: {response.chart}")
            except Exception as e:
                st.warning(f"Could not display chart: {e}")
