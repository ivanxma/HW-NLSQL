import pandas as pd
import streamlit as st

from mydbtools import (
    get_all_databases,
    get_configdb_databases,
    init_session_state,
    login_page,
    save_configdb_databases,
    setupDB,
    show_connection_status,
)


def _available_picker_key():
    return "configdb_available_picker_{}".format(st.session_state.configdb_picker_version)


def _selected_table_key():
    return "configdb_selected_table_{}".format(st.session_state.configdb_picker_version)


def _set_action_message(level, message):
    st.session_state.configdb_action_message = {"level": level, "message": message}


def _show_action_message():
    payload = st.session_state.pop("configdb_action_message", None)
    if not payload:
        return

    level = payload.get("level", "info")
    message = payload.get("message", "")
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)


def _get_selected_rows(table_state):
    if hasattr(table_state, "selection") and hasattr(table_state.selection, "rows"):
        return list(table_state.selection.rows)
    if isinstance(table_state, dict):
        return list(table_state.get("selection", {}).get("rows", []))
    return []


def _bump_picker_version():
    st.session_state.configdb_picker_version += 1
    st.session_state[_available_picker_key()] = []


def _init_configdb_state():
    if "configdb_picker_version" not in st.session_state:
        st.session_state.configdb_picker_version = 0
    if "configdb_available" in st.session_state and "configdb_selected" in st.session_state:
        st.session_state.setdefault(_available_picker_key(), [])
        return

    configured = sorted(set(get_configdb_databases()))
    available = [db_name for db_name in get_all_databases() if db_name not in configured]
    st.session_state.configdb_available = available
    st.session_state.configdb_selected = configured
    st.session_state[_available_picker_key()] = []


def _move_to_selected(chosen):
    if not chosen:
        return 0

    available = [db_name for db_name in st.session_state.configdb_available if db_name not in chosen]
    selected = sorted(set(st.session_state.configdb_selected).union(chosen))
    moved_count = len(selected) - len(st.session_state.configdb_selected)
    st.session_state.configdb_available = available
    st.session_state.configdb_selected = selected
    _bump_picker_version()
    return moved_count


def _move_to_available(chosen_rows):
    if not chosen_rows:
        return 0

    chosen = [
        st.session_state.configdb_selected[row_index]
        for row_index in chosen_rows
        if 0 <= row_index < len(st.session_state.configdb_selected)
    ]
    if not chosen:
        return 0

    selected = [db_name for db_name in st.session_state.configdb_selected if db_name not in chosen]
    available = sorted(set(st.session_state.configdb_available).union(chosen))
    removed_count = len(st.session_state.configdb_selected) - len(selected)
    st.session_state.configdb_available = available
    st.session_state.configdb_selected = selected
    _bump_picker_version()
    return removed_count


def _reload_from_db():
    configured = sorted(set(get_configdb_databases()))
    available = [db_name for db_name in get_all_databases() if db_name not in configured]
    st.session_state.configdb_available = available
    st.session_state.configdb_selected = configured
    _bump_picker_version()
    return len(configured)


def main():
    st.title("Setup configdb")
    show_connection_status()
    st.write("Move databases into the right-side list, then save the `nlsql.configdb` configuration.")

    _init_configdb_state()
    _show_action_message()

    left_col, middle_col, right_col = st.columns([5, 1.4, 5])
    available_selection = []
    selected_rows = []

    with left_col:
        st.subheader("Available Databases")
        available_selection = st.multiselect(
            "Database list",
            options=st.session_state.configdb_available,
            key=_available_picker_key(),
            label_visibility="collapsed",
            placeholder="No available databases",
        )

    with right_col:
        st.subheader("nlsql.configdb")
        selected_df = pd.DataFrame({"Database": st.session_state.configdb_selected})
        table_state = st.dataframe(
            selected_df,
            key=_selected_table_key(),
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
        )
        selected_rows = _get_selected_rows(table_state)

    with middle_col:
        st.write("")
        st.write("")
        if st.button("➕", key="configdb_add", use_container_width=True):
            moved_count = _move_to_selected(available_selection)
            if moved_count > 0:
                _set_action_message("success", "Added {} row(s) to nlsql.configdb selection.".format(moved_count))
            else:
                _set_action_message("warning", "No databases were added.")
            st.rerun()
        if st.button("➖", key="configdb_remove", use_container_width=True):
            removed_count = _move_to_available(selected_rows)
            if removed_count > 0:
                _set_action_message("success", "Removed {} row(s) from nlsql.configdb selection.".format(removed_count))
            else:
                _set_action_message("warning", "No table rows were selected for removal.")
            st.rerun()

    save_col, reload_col = st.columns([1.2, 1])
    with save_col:
        if st.button("Save", type="primary", use_container_width=True):
            if save_configdb_databases(st.session_state.configdb_selected):
                row_count = _reload_from_db()
                _set_action_message("success", "Saved {} row(s) to nlsql.configdb.".format(row_count))
                st.rerun()
            else:
                _set_action_message("error", "Failed to save nlsql.configdb.")
                st.rerun()
    with reload_col:
        if st.button("Reload", use_container_width=True):
            row_count = _reload_from_db()
            _set_action_message("info", "Reloaded {} row(s) from nlsql.configdb.".format(row_count))
            st.rerun()


st.set_page_config(page_title="Setup configdb", layout="wide")
init_session_state()

if not login_page():
    st.stop()

setupDB()
main()
