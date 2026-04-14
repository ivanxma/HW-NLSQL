import json

import pandas as pd
import streamlit as st

from mydbtools import (
    callProc,
    connectMySQL,
    getDB,
    getNLSQLLLMModel,
    init_session_state,
    login_page,
    setupDB,
    show_connection_status,
)


def call_nlsql(aquestion, allm, adb):
    with connectMySQL() as db:
        mydbs = ', '.join(['"{}"'.format(value) for value in adb])
        optString = '{{"execute":true, "model_id":"{llm}", "schemas":[{dblist}]}}'.format(
            llm=allm,
            dblist=mydbs,
        )
        args = [aquestion, "", optString]
        return callProc("sys.NL_SQL", args, db)


def main():
    st.title("HeatWave demo NL_SQL")
    show_connection_status()
    st.page_link(
        "https://dev.mysql.com/doc/heatwave/en/mys-hw-genai-nl-sql.html",
        label="NL_SQL Page",
        icon="🌎",
    )

    col1, col2 = st.columns(2)
    with col1:
        myquestion = st.text_input("Question")
        submitButton = st.button("Submit", width="stretch")
    with col2:
        databases = getDB()
        default_databases = [
            db_name
            for db_name in ("information_schema", "performance_schema")
            if db_name in databases
        ]
        db = st.multiselect("Choose DB", databases, default=default_databases)
        nlllmmodel = getNLSQLLLMModel()
        if not nlllmmodel:
            st.error("No supported generation models were found for this connection.")
            return
        default_model = "meta.llama-3.3-70b-instruct"
        default_index = nlllmmodel.index(default_model) if default_model in nlllmmodel else 0
        llm = st.selectbox("Choose LLM", nlllmmodel, index=default_index)

    if submitButton:
        if not myquestion.strip():
            st.warning("Enter a question.")
        elif not db:
            st.warning("Choose at least one schema.")
        else:
            ans = call_nlsql(myquestion, llm, db)
            if ans:
                outputarg = json.loads(ans["output"])
                resultset = ans["resultset"]
                columnset = ans["columnset"]

                if outputarg.get("is_sql_valid") == 1:
                    for i in range(len(resultset)):
                        mydf1 = pd.DataFrame(resultset[i], columns=columnset[i])
                        st.dataframe(mydf1)

                st.text_area("The SQL", outputarg.get("sql_query", ""), 100)
                st.text_area("The Tables", outputarg.get("tables", ""), 100)

    st.code(
        """
mysql> CALL sys.NL_SQL("NaturalLanguageStatement", @output[, options]);

  options: JSON_OBJECT(keyvalue[, keyvalue]...)
keyvalue:
{
  'execute', {true|false}
  | 'schemas', JSON_ARRAY('DBName'[, 'DBName'] ...)
  | 'tables', JSON_ARRAY(TableJSON[, TableJSON] ...)
  | 'model_id', 'ModelID'
  | 'verbose', {0|1|2}
  | 'include_comments', {true|false}
  | 'use_retry', {true|false}
}
""",
        language=None,
    )


st.set_page_config(page_title="HeatWave Demo - NLSQL", layout="wide")
init_session_state()

if not login_page():
    st.stop()

setupDB()
main()
