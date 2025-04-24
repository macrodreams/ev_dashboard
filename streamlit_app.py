import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import openai
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

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
