import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("cleaned_ev_data.csv")

st.set_page_config(page_title="EV Charging Stations Dashboard", layout="wide")
st.title("🔌 EV Charging Stations - San Jose")
st.markdown("""
Welcome to the EV Charging Station Dashboard! Explore charging station availability, vendor presence, and neighborhood distribution in San Jose.
""")

# Top EV Vendors
st.subheader("Top EV Vendors")
vendor_counts = df["EV Vendor"].value_counts().head(10)
fig1, ax1 = plt.subplots(figsize=(8, 5))
sns.barplot(y=vendor_counts.index, x=vendor_counts.values, ax=ax1, palette="viridis")
ax1.set_xlabel("Number of Stations")
ax1.set_ylabel("EV Vendor")
st.pyplot(fig1)

# Stations by Neighborhood
st.subheader("EV Stations by Neighborhood")
neighborhood_counts = df["neighborhood"].value_counts().head(10)
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(y=neighborhood_counts.index, x=neighborhood_counts.values, ax=ax2, palette="mako")
ax2.set_xlabel("Number of Stations")
ax2.set_ylabel("Neighborhood")
st.pyplot(fig2)

# Optional: Vendor Filter
ev_vendors = df["EV Vendor"].unique()
selected_vendor = st.selectbox("Filter by EV Vendor", ["All"] + list(ev_vendors))
if selected_vendor != "All":
    filtered_df = df[df["EV Vendor"] == selected_vendor]
    st.write(f"Showing {len(filtered_df)} stations for vendor: **{selected_vendor}**")
    st.dataframe(filtered_df[["address", "neighborhood", "city", "rank", "totalScore", "reviewsCount"]])
else:
    st.write("Showing all EV charging stations")
