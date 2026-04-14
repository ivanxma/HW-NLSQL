import streamlit as st

from mydbtools import (
    get_connection_profile,
    get_connection_summary,
    init_session_state,
    isValid_user,
    set_connection_profile,
)


def main():
    st.title("Setup Connection Profile")
    st.write(
        "This page stores only the connection profile in Streamlit session state. "
        "Database credentials are entered at login time and are not kept in source files."
    )

    profile = get_connection_profile()

    with st.form("connection_profile_form"):
        host = st.text_input("Host", value=profile["host"])
        port = st.number_input(
            "Port",
            min_value=1,
            max_value=65535,
            value=int(profile["port"]),
            step=1,
        )
        database = st.text_input("Default database", value=profile["database"])
        submitted = st.form_submit_button("Save connection profile")

        if submitted:
            set_connection_profile(host, int(port), database)
            st.success("Connection profile saved for this session.")

    st.caption("Current profile: {}".format(get_connection_summary()))
    st.divider()

    st.subheader("Optional connection test")
    with st.form("connection_test_form"):
        test_user = st.text_input("Database user")
        test_password = st.text_input("Database password", type="password")
        test_submitted = st.form_submit_button("Test connection")

        if test_submitted:
            if not test_user or not test_password:
                st.warning("Enter both the database user and password to test the profile.")
            elif isValid_user(test_user, test_password):
                st.success("Connection test succeeded.")
            else:
                st.error("Connection test failed.")


st.set_page_config(page_title="Setup Connection Profile", layout="wide")
init_session_state()
main()
