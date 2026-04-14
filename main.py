import streamlit as st

from mydbtools import (
    get_connection_summary,
    init_session_state,
    login_page,
    show_connection_status,
    clear_login_state,
)


def main():
    init_session_state()

    if not st.session_state.logged_in:
        login_page()
        return

    st.header("HeatWave Demo")
    st.divider()
    show_connection_status()
    st.write("This demo uses HeatWave GenAI features on your configured MySQL connection.")
    st.write("Use the sidebar menu to switch between the application pages.")

    st.page_link(
        "pages/00_Connection_Profile.py",
        label="Setup Connection Profile",
        icon=":material/settings:",
    )
    st.page_link(
        "pages/01_Setup_ConfigDB.py",
        label="Setup configdb",
        icon=":material/tune:",
    )
    st.page_link("pages/HWnlsql.py", label="HWnlsql", icon=":material/database:")
    st.page_link("pages/HWVision.py", label="HWVision", icon=":material/image:")

    if st.button("Logout", type="secondary"):
        clear_login_state()
        st.rerun()

    st.divider()
    st.caption("Active profile: {}".format(get_connection_summary()))


st.set_page_config(page_title="HeatWave Demo", layout="wide")
main()
