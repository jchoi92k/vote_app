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
DEFAULT = "No opinion"

# Helper function
def divide_list(input_list, n):
   return [input_list[i:i + n] for i in range(0, len(input_list), n)]

st.set_page_config(layout="wide")

image_list = os.listdir(r"imgs")
image_cols = divide_list(image_list, COL_NUM)

@st.cache_data
def imgload(sub_item):
   return Image.open(os.path.join("imgs", sub_item))

c = st.container()
cnd = dict()

with c:
   st.header("LEAR Voting App")
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

for item in image_cols:
   cols = st.columns(COL_NUM)
   for i, sub_item in enumerate(item):
      img = imgload(sub_item)
      with cols[i]:
         st.image(img, use_column_width="always")
         sub_item = sub_item[:-4]
         st.selectbox(label=r"Your impression:", options=(DEFAULT, "Hate it", "Not great", "It's okay", "Like it", "Love it"), key=f"{sub_item}")
