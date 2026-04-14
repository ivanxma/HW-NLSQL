# HeatWave Demo

This Streamlit application demonstrates HeatWave GenAI features for NL-SQL and vision prompts.

## Install

```bash
pip install streamlit mysql-connector-python pandas pillow
```

## Run

Start the app with HTTPS on port `443`:

```bash
./start_https.sh
```

The launcher generates a self-signed certificate under `.streamlit/certs/` if one does not already exist.
If port `443` requires elevated privileges on your host, the script re-runs itself with `sudo`.

## Configure

1. Open the app.
2. Use the sidebar menu item `Setup Connection Profile`.
3. Save the MySQL host, port, and default database.
4. Return to `Home` and log in with the database user and password.
5. Use `Setup configdb` to choose which schemas should be available to the NL-SQL page.

The application no longer uses `globalvar.py`, and credentials are not stored in source files.
