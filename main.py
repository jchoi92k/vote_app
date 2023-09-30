import streamlit as st
import os
import pandas as pd
from PIL import Image
from collections import Counter
from supabase import create_client, Client
import json

try:
   from config import URI, KEE
   url: str = URI
   key: str = KEE
except Exception:
   url: str = st.secrets["URI"]
   key: str = st.secrets["KEE"]

supabase: Client = create_client(url, key)

COL_NUM = 5
TOP_K = 10
DEFAULT = "No opinion"
SCORES = {"Hate it": -2, "Not great": -1, "It's okay": 1, "Like it": 2, "Love it": 3}

# Define a mapping of vote categories to scores
vote_scores = {
    "Hate it": -2,
    "Not great": -1,
    "It's okay": 1,
    "Like it": 2,
    "Love it": 3,
}


# Helper function
def divide_list(input_list, n):
   return [input_list[i:i + n] for i in range(0, len(input_list), n)]

st.set_page_config(layout="wide")

image_list = os.listdir(r"imgs")
image_cols = divide_list(image_list, COL_NUM)

@st.cache_data
def imgload(sub_item):
   return Image.open(os.path.join("imgs", sub_item))

st.header("LEAR Voting App")

cnd = dict()
tab1, tab2 = st.tabs(["Vote", "View Results"])

with tab1:
   st.subheader("Vote")
   st.write("Scroll through the page. Mark any items that you have strongish opinions on using the drop down menu. Press CLEAR if you want to restart. Enter your name and press SUBMIT when you've finalized your choice.")
   writes = "Current choices = "
   if list(st.session_state.keys()) != []:
      cdict = dict(Counter(st.session_state.values()))
      for k, v in cdict.items():
         if k != DEFAULT:
            writes = writes + f"|| {k}: {v} || "
   st.caption(writes)

   yourname = st.text_input("Your name", "Anonymous")

   but_cols = st.columns(12)

   with but_cols[0]:
      if st.button("SUBMIT"):
         supabase.table('votes').insert({"user":yourname, "votes": json.dumps(dict(st.session_state))}).execute()
         st.experimental_rerun()

   with but_cols[1]:
      if st.button("CLEAR"):
         st.experimental_rerun()

with tab2:
   st.subheader("View Results")
   scorecritstring = f"Top {TOP_K} results. Scoring metric is as follows "
   for key, value in vote_scores.items():
      scorecritstring += f" {key}: {value}, "
   df = pd.DataFrame(supabase.table('votes').select("*").execute().data)
   dfunique = df.sort_values("created_at").drop_duplicates(["user"], keep="last")

   # Create an empty dictionary to store aggregated scores
   aggregated_scores = {}

   # Iterate through each participant's vote dictionary
   for participant_vote in list(dfunique['votes']):
       participant_vote = json.loads(participant_vote)
       # Iterate through items and votes in the participant's vote
       for item, vote in participant_vote.items():
           # Check if the vote is not "No opinion"
           if vote != "No opinion":
               # Add the numeric score to the aggregated scores
               aggregated_scores[item] = aggregated_scores.get(item, 0) + vote_scores.get(vote, 0)

   # Sort the items in the aggregated_scores dictionary by their scores (in descending order)
   sorted_items = sorted(aggregated_scores.items(), key=lambda x: x[1], reverse=True)

   # Take the top 5 items
   top_k_items = sorted_items[:TOP_K]

   top_k_cols = st.columns(TOP_K)
   for i1, si in enumerate(top_k_items):
      with top_k_cols[i1]:
         img = imgload(f"{si[0]}.jpg")
         st.image(img, use_column_width="always")
         st.write(f"Rank {i1+1} || Score: {si[1]}")

st.write("---")

for item in image_cols:
   cols = st.columns(COL_NUM)
   for i, sub_item in enumerate(item):
      img = imgload(sub_item)
      with cols[i]:
         st.image(img, use_column_width="always")
         sub_item = sub_item[:-4]
         st.selectbox(label=r"Your impression:", options=(DEFAULT, "Hate it", "Not great", "It's okay", "Like it", "Love it"), key=f"{sub_item}")
