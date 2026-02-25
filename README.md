# This is demo for GenAI NL_SQL and VISION LLM

1. Install streamlit : https://docs.streamlit.io/get-started/installation
```
pip install streamlit
streamlit hello
```
2. Install mysql-connector-python : https://dev.mysql.com/doc/connector-python/en/connector-python-installation-binary.html
```
pip install mysql-connector-python
```
3. Install pandas : https://pandas.pydata.org/docs/getting_started/install.html
```
pip install pandas
```
4. create globalvar.py which to include the following
```
myconfig = {
    "user":"",
    "password":"",
    "host":"",
    "port":3306,
    "database": ""
}
```

5. run it
```
  streamlit run main.py
```
