import mysql.connector
import streamlit as st
from mysql.connector import errorcode


DEFAULT_CONNECTION_PROFILE = {
    "host": "",
    "port": 3306,
    "database": "performance_schema",
}


def init_session_state():
    if "connection_profile" not in st.session_state:
        st.session_state.connection_profile = DEFAULT_CONNECTION_PROFILE.copy()
    if "db_user" not in st.session_state:
        st.session_state.db_user = ""
    if "db_password" not in st.session_state:
        st.session_state.db_password = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False


def _normalized_port(port_value):
    try:
        return int(port_value)
    except (TypeError, ValueError):
        return DEFAULT_CONNECTION_PROFILE["port"]


def get_connection_profile():
    init_session_state()
    profile = st.session_state.connection_profile
    return {
        "host": str(profile.get("host", "")).strip(),
        "port": _normalized_port(profile.get("port")),
        "database": str(profile.get("database", "")).strip(),
    }


def clear_login_state():
    init_session_state()
    st.session_state.logged_in = False
    st.session_state.db_user = ""
    st.session_state.db_password = ""


def set_connection_profile(host, port, database):
    init_session_state()
    new_profile = {
        "host": str(host).strip(),
        "port": _normalized_port(port),
        "database": str(database).strip(),
    }
    if new_profile != get_connection_profile():
        clear_login_state()
    st.session_state.connection_profile = new_profile


def is_connection_profile_complete():
    profile = get_connection_profile()
    return bool(profile["host"] and profile["database"] and profile["port"])


def get_connection_summary():
    profile = get_connection_profile()
    if not is_connection_profile_complete():
        return "Not configured"
    return "{host}:{port}/{database}".format(**profile)


def get_connection_config(user=None, password=None, include_database=True):
    profile = get_connection_profile()
    config = {
        "host": profile["host"],
        "port": profile["port"],
    }
    if include_database and profile["database"]:
        config["database"] = profile["database"]

    resolved_user = st.session_state.get("db_user", "") if user is None else user
    resolved_password = (
        st.session_state.get("db_password", "") if password is None else password
    )

    if resolved_user:
        config["user"] = resolved_user
    if resolved_password:
        config["password"] = resolved_password

    return config


def connectMySQL(myconfig=None):
    config = myconfig or get_connection_config()
    return mysql.connector.connect(**config)


def callProc(theProc, args, cnx):
    dataset = []
    columnset = []
    try:
        with cnx.cursor() as cursor:
            result_args = cursor.callproc(theProc, args)
            for result in cursor.stored_results():
                rows = result.fetchall()
                columns = result.column_names
                dataset.append(rows)
                columnset.append(columns)
    except Exception as error:
        print("Error calling SP", error)
        return None

    return {
        "output": result_args[1],
        "resultset": dataset,
        "columnset": columnset,
    }


def execSQL(theSQL, cnx, params=None):
    cursor = cnx.cursor()
    try:
        cursor.execute(theSQL, params or ())
        cnx.commit()
    except mysql.connector.Error as error:
        cnx.rollback()
        print("executing SQL failure : {}".format(error))
    finally:
        if cnx.is_connected():
            cursor.close()


def runSQL(theSQL, cnx, params=None):
    cursor = cnx.cursor()
    try:
        cursor.execute(theSQL, params or ())
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print("executing SQL failure : {}".format(error))
        return None
    finally:
        if cnx.is_connected():
            cursor.close()


def _get_model_ids(query):
    cnx = None
    try:
        cnx = connectMySQL()
        data = runSQL(query, cnx)
        if not data:
            return tuple()
        return tuple(row[0] for row in data)
    except Exception as error:
        print("Error while reading supported models : ", error)
        return tuple()
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def getEmbModel():
    return _get_model_ids(
        """
        select model_id
        from sys.ML_SUPPORTED_LLMS
        where capabilities->>'$[0]'='TEXT_EMBEDDINGS'
        """
    )


def getLLMModel():
    return _get_model_ids(
        """
        select model_id
        from sys.ML_SUPPORTED_LLMS
        where capabilities->>'$[0]'='GENERATION'
        """
    )


def getVisionLLMModel():
    return _get_model_ids(
        """
        select model_id
        from sys.ML_SUPPORTED_LLMS
        where capabilities->>'$[0]'='GENERATION'
        """
    )


def getNLSQLLLMModel():
    return _get_model_ids(
        """
        select model_id
        from sys.ML_SUPPORTED_LLMS
        where capabilities->>'$[0]'='GENERATION'
        """
    )


def getDB():
    cnx = None
    try:
        cnx = connectMySQL()
        data = runSQL(
            """
            select schema_name
            from information_schema.schemata
            where schema_name in (
                select db_name
                from nlsql.configdb
                where enabled = 'Y'
            )
            order by schema_name
            """,
            cnx,
        )
        if not data:
            return tuple()
        return tuple(row[0] for row in data)
    except Exception as error:
        print("Error while reading DB config : ", error)
        return tuple()
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def get_all_databases():
    cnx = None
    try:
        cnx = connectMySQL(get_connection_config(include_database=False))
        data = runSQL(
            """
            select schema_name
            from information_schema.schemata
            where schema_name <> 'nlsql'
            order by schema_name
            """,
            cnx,
        )
        if not data:
            return tuple()
        return tuple(row[0] for row in data)
    except Exception as error:
        print("Error while reading available databases : ", error)
        return tuple()
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def get_configdb_databases():
    cnx = None
    try:
        cnx = connectMySQL(get_connection_config(include_database=False))
        data = runSQL(
            """
            select db_name
            from nlsql.configdb
            where enabled = 'Y'
            order by db_name
            """,
            cnx,
        )
        if not data:
            return tuple()
        return tuple(row[0] for row in data)
    except Exception as error:
        print("Error while reading configdb databases : ", error)
        return tuple()
    finally:
        if cnx and cnx.is_connected():
            cnx.close()


def save_configdb_databases(database_names):
    cnx = None
    cursor = None
    try:
        cnx = connectMySQL(get_connection_config(include_database=False))
        cursor = cnx.cursor()
        cursor.execute("delete from nlsql.configdb")
        if database_names:
            cursor.executemany(
                """
                insert into nlsql.configdb (db_name, enabled)
                values (%s, 'Y')
                """,
                [(db_name,) for db_name in database_names],
            )
        cnx.commit()
        return True
    except mysql.connector.Error as error:
        if cnx:
            cnx.rollback()
        print("saving configdb failure : {}".format(error))
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def show_connection_status():
    init_session_state()
    st.caption("Connection profile: {}".format(get_connection_summary()))


def login_page():
    init_session_state()
    if st.session_state.logged_in:
        return True

    if not is_connection_profile_complete():
        st.warning("Set up the connection profile before logging in.")
        st.page_link(
            "pages/00_Connection_Profile.py",
            label="Open Setup Connection Profile",
            icon=":material/settings:",
        )
        return False

    show_connection_status()
    login_page_container = st.empty()
    with login_page_container.container():
        st.title("HeatWave Demo - Login Page")
        with st.form("login_form"):
            username = st.text_input("Database user", value=st.session_state.db_user)
            password = st.text_input("Database password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if isValid_user(username, password):
                    st.session_state.db_user = username
                    st.session_state.db_password = password
                    st.session_state.logged_in = True
                    st.success("Login successful.")
                    st.rerun()
                else:
                    clear_login_state()
                    st.error("Invalid connection profile or database credentials.")

    return st.session_state.logged_in


def isValid_user(user, password):
    config = get_connection_config(
        user=user,
        password=password,
        include_database=bool(get_connection_profile()["database"]),
    )
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return False
    else:
        cnx.close()
        return True


def setupDB():
    cnx = None
    try:
        cnx = connectMySQL(get_connection_config(include_database=False))
        execSQL(
            """
            create database if not exists nlsql;
            """,
            cnx,
        )
        execSQL(
            """
            create table if not exists nlsql.configdb (
                db_name varchar(64) not null primary key,
                enabled char(1) not null
            );
            """,
            cnx,
        )
        execSQL(
            """
            insert into nlsql.configdb (db_name, enabled)
            select x.schema_name, 'Y'
            from (
                select 'information_schema' as schema_name
                union all
                select 'sys'
                union all
                select 'performance_schema'
            ) x
            left join nlsql.configdb y
                on x.schema_name = y.db_name
            where y.db_name is null;
            """,
            cnx,
        )
        return True
    except Exception as error:
        print("Error while setup in DB : ", error)
        return False
    finally:
        if cnx and cnx.is_connected():
            cnx.close()
