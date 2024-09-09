import streamlit as st
import time
import os
from src.st_funcs import test_func

st.title("Sample App")

st.write("Hello, World!")

if st.button("Click me"):
  test_func()

