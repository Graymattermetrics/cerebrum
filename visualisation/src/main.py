import os
import streamlit as st
import pandas as pd


def open_db():
    """Open the SQLite database."""
    import sqlite3

    conn = sqlite3.connect("/data/db.sqlite")
    return conn


st.set_page_config(page_title="Cerebrum Visualisation", layout="wide")
st.title("Cerebrum Visualisation Dashboard")
st.markdown("This dashboard visualises data from the Cerebrum database.")


def authenticate():
    password = st.text_input("Enter password", type="password")
    if password != os.environ["SQLITE_WEB_PASSWORD"]:
        st.warning("Incorrect password")
        st.stop()


connection = open_db()


def generate_age_chart():
    clients = connection.execute(
        "SELECT full_name, date_of_birth FROM clients"
    ).fetchall()
    if not clients:
        st.warning("No clients found in the database.")
        st.stop()
    date_of_birth = pd.to_datetime([client[1] for client in clients])
    clients = [
        (client[0], max((pd.Timestamp.now() - dob).days // 365, 13))
        for client, dob in zip(clients, date_of_birth)
    ]
    clients_df = pd.DataFrame(clients, columns=["Name", "Age"])
    st.title("Clients Age Chart")
    st.title("Cerebrum Visualisation")

    tab1, tab2 = st.tabs(["Chart", "Dataframe"])
    tab1.bar_chart(clients_df.set_index("Name"), height=250)
    tab2.dataframe(clients_df, height=250, use_container_width=True)


def generate_cogspeed_test_results_chart():
    clients = connection.execute("SELECT full_name, client_id FROM clients").fetchall()
    client_name = st.selectbox("Select Client", [client[0] for client in clients])
    if not client_name:
        st.warning("Please select a client.")
        st.stop()

    client_id = next(client[1] for client in clients if client[0] == client_name)
    cogspeed_results = connection.execute(
        "SELECT date, blocking_round_duration FROM cogspeed_test_results WHERE client_id = ?",
        (client_id,),
    ).fetchall()

    if not cogspeed_results:
        st.warning(f"No Cogspeed test results found for {client_name}.")
        st.stop()

    cogspeed_df = pd.DataFrame(cogspeed_results, columns=["Test Date", "Score"])
    cogspeed_df["Test Date"] = pd.to_datetime(cogspeed_df["Test Date"])
    cogspeed_df.set_index("Test Date", inplace=True)
    st.title(f"Cogspeed Test Results for {client_name}")

    tab1, tab2 = st.tabs(["Chart", "Dataframe"])
    tab1.line_chart(cogspeed_df["Score"], height=250)
    tab2.dataframe(cogspeed_df, height=250, use_container_width=True)


authenticate()
generate_age_chart()
generate_cogspeed_test_results_chart()
