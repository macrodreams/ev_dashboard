import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import openai

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

# File uploader
uploaded_file = st.file_uploader("Upload cleaned_ev_data.csv", type=["csv"])
if uploaded_file is not None:
    EV_df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    st.dataframe(EV_df.head())
else:
    st.info("Please upload your cleaned_ev_data.csv file to proceed.")
    st.stop()

system_prompt = """
You are a data analyst for EV charging station insights.
Avoid using restricted matplotlib functions like `gca()` or `tight_layout`.
Only use simple plotting code that works in safe environments like PandasAI.
If a chart is requested, prefer using basic bar or line plots only.
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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": safe_output}
        ]
    )
    return response.choices[0].message.content.strip()

# User prompt
user_prompt = st.text_area("Ask a question about the EV charging station data:")

if st.button("Submit Query") and user_prompt:
    with st.spinner("Processing your query..."):
        refined = refine_prompt(user_prompt)
        response = EV_SmartDF.chat(refined)
        final_response = clean_llm_output(response)
    st.subheader("LLM Response:")
    st.write(final_response)
    if hasattr(response, 'chart') and response.chart is not None:
        st.pyplot(response.chart)
