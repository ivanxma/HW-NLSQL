import streamlit as st
from mydbtools import *




def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()

    if st.session_state.logged_in:
       st.header("HeatWave Demo")   
       st.divider()
       st.write("This is a DEMO using HeatWave 9.4.1+ on OCI")
       st.write("1. HWnlsql : The Natural Language to SQL")
       st.write("1. HWvision : Upload Image for vision LLM")
       st.divider()
       # You can put your main app content here
       # st.write("You are logged in!")

if __name__ == "__main__":
    main()

            
