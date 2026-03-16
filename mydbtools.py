import streamlit as st
import globalvar
import mysql.connector
from mysql.connector import errorcode

# MySQL Connectoin Profile
myconfig = globalvar.myconfig

# Used to connect to MySQL
def connectMySQL(myconfig) :
    cnx = mysql.connector.connect(**myconfig)
    return cnx

def callProc(theProc, args, cnx) :

    dataset=[]
    columnset=[]
    try : 
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

    returnvar={}
    returnvar['output'] = result_args[1]
    returnvar['resultset'] = dataset
    returnvar['columnset'] = columnset
    return returnvar



def runSQL(theSQL, cnx ) :
    cursor = cnx.cursor()
    try : 
           cursor.execute(theSQL)
           data = cursor.fetchall()
           return data

    except mysql.connector.Error as error:
        print("executing SQL failure : {}".format(error))
    finally:
            if cnx.is_connected():
                cursor.close()

def getEmbModel() :
    cnx = connectMySQL(myconfig)
    embModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='TEXT_EMBEDDINGS'
        """, cnx )
        for row in data:
           embModels.append(row[0])

    except Exception as error:
        embModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(embModels)

def getLLMModel() :
    cnx = connectMySQL(myconfig)
    llmModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION'
        """, cnx )
        for row in data:
           llmModels.append(row[0])

    except Exception as error:
        llmModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(llmModels)

def getVisionLLMModel() :
    cnx = connectMySQL(myconfig)
    llmModels=[]
    try:
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION' and model_id like '%vision%'
        """, cnx)
        for row in data:
           llmModels.append(row[0])

    except Exception as error:
        llmModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(llmModels)

def getNLSQLLLMModel() :
    cnx = connectMySQL(myconfig)
    llmModels=[]
    try:
          # select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION' and model_id in ('meta.llama-3.3-70b-instruct', 'meta.llama-3.3-70b-instruct', 'llama3.1-8b-instruct-v1', 'llama3.2-3b-instruct-v1')
        data = runSQL("""
          select model_id, capabilities->>'$[0]' from sys.ML_SUPPORTED_LLMS where capabilities->>'$[0]'='GENERATION'
        """, cnx)
        for row in data:
           llmModels.append(row[0])

    except Exception as error:
        llmModels=[]
        print("Error while inserting in DB : ", error)

    return tuple(llmModels)


def getDB() :
    cnx = connectMySQL(myconfig)
    mylist=[]
    try:
        data = runSQL("""
          select schema_name from information_schema.schemata  where schema_name in (SELECT db_name FROM nlsql.configdb );
        """, cnx)
        for row in data:
           mylist.append(row[0])

    except Exception as error:
        mylist=[]
        print("Error while inserting in DB : ", error)

    return tuple(mylist)




def login_page():
    if 'logged_in' in st.session_state :
        if st.session_state.logged_in:
            return True
    st.session_state.logged_in = False
    loginPage = st.empty()
    with loginPage.container():
      st.title("Heatwave Demo - Login Page")
      with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # Replace this with your actual authentication logic
            if isValid_user(username, password):
                st.success("Login successful!")
                # You can redirect to another page or perform some action here
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password")
                st.session_state.logged_in = False
    if st.session_state.logged_in :
      loginPage.empty()
      return True
    else:
      return False



def isValid_user(user, password):
    myconfig['user'] = user
    myconfig['password'] = password

    try:
        cnx = mysql.connector.connect(**myconfig)
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

def setupDB() :

    cnx = connectMySQL(myconfig)
    try:
        data = runSQL("""
          create database if not exists nlsql;
          create table if not exists nlsql.configdb (db_name varchar(64) not null primary key, enabled char(1) not null);
          select x.* from (SELECT schema_name AS 'database', 'Y' AS has_it FROM ( VALUES ROW('information_schema'), ROW('sys'), ROW('performance_schema')) AS t(schema_name)) x left join nlsql.configdb y on (x.database = y.db_name) where y.db_name is null;
        """, cnx)

    except Exception as error:
        print("Error while setup in DB : ", error)
        return False

    return True
