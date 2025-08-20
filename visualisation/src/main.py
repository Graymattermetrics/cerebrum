# pyright: basic

import os
from typing import Literal
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

from utils import create_hash, format_string


def open_db():
    """Open the SQLite database."""
    import sqlite3

    conn = sqlite3.connect("/data/db.sqlite")
    return conn


st.set_page_config(page_title="Cogspeed Visualisation", layout="wide", page_icon="⚙️")
st.title("Cogspeed Visualisation Dashboard")
st.markdown("This dashboard visualises data from the Cogspeed database.")


def authenticate_admin():
    password = st.text_input("Enter password", type="password")
    button = st.button("Admin Login")
    if not button:
        st.stop()

    if password != os.environ["SQLITE_WEB_PASSWORD"]:
        st.warning("Incorrect password")
        st.stop()
    st.success("Welcome Admin!")


def authenticate_client() -> str:
    email = st.text_input("Enter your email address")
    password = st.text_input("Enter password", type="password")
    password_hash = create_hash(password)

    button = st.button("Login")
    if not button:
        st.stop()

    if not email or not password:
        st.warning("Please enter both email and password")
        st.stop()

    if password == os.environ["SQLITE_WEB_PASSWORD"]:
        client = connection.execute(
            "SELECT full_name, client_id FROM clients WHERE email=?", (email,)
        ).fetchone()
    else:
        client = connection.execute(
            "SELECT full_name, client_id FROM clients WHERE email=? AND password_hash=?",
            (email, password_hash),
        ).fetchone()

    if not client:
        st.warning("Invalid email or password")
        st.stop()
    st.success(f"Welcome {client[0]}!")
    return client[1]


def generate_admin_client_chart(
    key: Literal["gender", "age", "country", "handedness"],
) -> None:
    if key == "age":
        clients_data = connection.execute(
            "SELECT date_of_birth FROM clients"
        ).fetchall()
        dates_of_birth = pd.to_datetime([client[0] for client in clients_data])
        ages = [
            max((pd.Timestamp.now() - dob).days // 365, 13) for dob in dates_of_birth
        ]
        data_series = pd.Series(ages, name="Age")

    else:
        assert key in ("gender", "country", "handedness"), "Preventing SQL injection"
        clients_data = connection.execute(f"SELECT {key} FROM clients").fetchall()
        data = [client[0] for client in clients_data]
        data_series = pd.Series(data, name=key.capitalize())

    aggregated_df = data_series.value_counts().reset_index()
    aggregated_df.columns = [key.capitalize(), "Count"]

    if key == "age":
        aggregated_df = aggregated_df.sort_values(by="Age").reset_index(drop=True)

    tab1, tab2 = st.tabs(["Chart", "Dataframe"])
    with tab1:
        st.bar_chart(
            data=aggregated_df.set_index(key.capitalize()),
            y="Count",
            x_label=key.capitalize(),
            y_label="Number of Clients",
        )
    with tab2:
        st.dataframe(aggregated_df)


def generate_cogspeed_test_results_chart(
    client_id: str,
    key: Literal[
        "blocking_round_duration", "test_duration", "number_of_rounds", "fatigue_level"
    ],
) -> None:
    assert key in (
        "blocking_round_duration",
        "test_duration",
        "number_of_rounds",
        "fatigue_level",
    ), "Preventing SQL injection"
    cogspeed_results = connection.execute(
        f"SELECT date, {key} FROM cogspeed_test_results WHERE client_id = ?",
        (client_id,),
    ).fetchall()

    if not cogspeed_results:
        st.warning("No Cogspeed test results found.")
        st.stop()

    keyf = format_string(key)
    cogspeed_df = pd.DataFrame(cogspeed_results, columns=["Test Date", keyf])
    cogspeed_df["Test Date"] = pd.to_datetime(cogspeed_df["Test Date"])
    cogspeed_df.set_index("Test Date", inplace=True)

    tab1, tab2 = st.tabs(["Chart", "Dataframe"])
    tab1.scatter_chart(cogspeed_df[keyf], x_label="Date", y_label=keyf)
    tab2.dataframe(cogspeed_df)


connection = open_db()

with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Admin"],
        icons=["house", "gear"],
        default_index=0,
    )

if selected == "Home":
    st.header("Client View")

    client_id = authenticate_client()

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with st.container():
        c1.write("BRD")
        c2.write("Test Duration")

    with st.container():
        c3.write("Number of Rounds")
        c4.write("Fatigue Level")

    with c1:
        generate_cogspeed_test_results_chart(client_id, key="blocking_round_duration")
    with c2:
        generate_cogspeed_test_results_chart(client_id, key="test_duration")
    with c3:
        generate_cogspeed_test_results_chart(client_id, key="number_of_rounds")
    with c4:
        generate_cogspeed_test_results_chart(client_id, key="fatigue_level")

if selected == "Admin":
    authenticate_admin()

    st.header("Admin View")

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with st.container():
        c1.write("Gender Distribution")
        c2.write("Age Distribution")

    with st.container():
        c3.write("Country Distribution")
        c4.write("Handedness Distribution")

    with c1:
        generate_admin_client_chart(key="gender")
    with c2:
        generate_admin_client_chart(key="age")
    with c3:
        generate_admin_client_chart(key="country")
    with c4:
        generate_admin_client_chart(key="handedness")

    clients = connection.execute("SELECT full_name, client_id FROM clients").fetchall()
    client_name = st.selectbox("View all clients", [client[0] for client in clients])
