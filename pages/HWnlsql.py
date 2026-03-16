import streamlit as st
import mysql.connector
import pandas as pd
import globalvar
from mydbtools import *
import json

# https://dev.mysql.com/doc/heatwave/en/mys-hwgenai-nl-sql.html

# MySQL Connectoin Profile
myconfig = globalvar.myconfig


def call_nlsql(aquestion, allm, adb):
           
   with connectMySQL(myconfig) as db:

   	cursor = db.cursor()
   	mydbs = ', '.join(['"{}"'.format(value) for value in adb])

   	myquery = """
   	CALL sys.NL_SQL("{question}", @output, JSON_OBJECT("execute",true, "model_id","{llm}", "schemas",JSON_ARRAY({dblist})));
   	""".format(question=aquestion, llm=allm, dblist=mydbs)
   	st.write(myquery)


   	optString = '{{"execute":true, "model_id":"{llm}", "schemas":[{dblist}]}}'.format(llm=allm, dblist=mydbs)

   	output_var = ""
   	args = [aquestion, output_var, optString]

   	result = callProc("sys.NL_SQL", args, db)
        
   	return result

    
# Set title
def main() :
  st.title("📷 HeatWave demo NL_SQL") 
  st.page_link('https://dev.mysql.com/doc/heatwave/en/mys-hw-genai-nl-sql.html', label="NL_SQL Page", icon="🌎")
  
  col1, col2 = st.columns(2)
  with col1 :
    myquestion = st.text_input("Question about the image")
    submitButton = st.button('Submit', use_container_width=True)
  with col2 :
    db = st.multiselect('Choose DB : ', getDB(), default=[ "information_schema", "performance_schema"]  )
    nlllmmodel = getNLSQLLLMModel()
    myindex = nlllmmodel.index('meta.llama-3.3-70b-instruct')
    llm = st.selectbox('Choose LLM : ', nlllmmodel, index=myindex)
  if submitButton :
          # Now you can use `img_base64` variable as needed
          ans = call_nlsql(myquestion, llm, db)
          if ans :
            outputarg = json.loads(ans['output'])
            resultset = ans['resultset']
            columnset = ans['columnset']
  
            isValidSQL = outputarg['is_sql_valid'] 
            if isValidSQL == 1 :
              mydf = pd.DataFrame(resultset[1], columns=columnset[1])
              st.dataframe(mydf)
            st.text_area("The SQL", outputarg['sql_query'], 100)
            st.text_area("The Tables", outputarg['tables'], 100)
  
  
  st.code("""
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
  """, language=None)
  

st.set_page_config(page_title="HeatWave Demo - NLSQL", layout="wide")
st.session_state.logged_in = login_page()

if st.session_state.logged_in:
      setupDB()
      main()

