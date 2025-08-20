# pyright: basic

import os
from typing import Literal

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from utils import create_hash, format_string, mean_ci


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


def generate_time_of_day_chart(client_id: str) -> None:
    """Plots 2 datasets on the same graph, results (blocking round duration)
    in the morning and results in the evening.
    """
    morning_results = connection.execute(
        "SELECT date, blocking_round_duration FROM cogspeed_test_results WHERE "
        "strftime('%H', date) BETWEEN '06' AND '11' AND client_id=?",
        (client_id,),
    ).fetchall()
    evening_results = connection.execute(
        "SELECT date, blocking_round_duration FROM cogspeed_test_results WHERE "
        "strftime('%H', date) BETWEEN '17' AND '22' AND client_id=?",
        (client_id,),
    ).fetchall()

    if not morning_results or not evening_results:
        st.warning("No Cogspeed test results found for the specified time periods.")
        st.stop()

    morning_df = pd.DataFrame(morning_results, columns=["Test Date", "Morning BRD"])
    evening_df = pd.DataFrame(evening_results, columns=["Test Date", "Evening BRD"])

    morning_df["Morning BRD"] = morning_df["Morning BRD"].round(3)
    evening_df["Evening BRD"] = evening_df["Evening BRD"].round(3)

    morning_df["Test Date"] = pd.to_datetime(morning_df["Test Date"])
    evening_df["Test Date"] = pd.to_datetime(evening_df["Test Date"])

    combined_df = pd.merge(morning_df, evening_df, on="Test Date", how="outer")

    chart = (
        alt.Chart(combined_df.melt("Test Date", var_name="Period", value_name="BRD"))
        .mark_line(point=True)
        .encode(
            x="Test Date:T",
            y="BRD:Q",
            color="Period:N",
            tooltip=[
                alt.Tooltip("Test Date:T", title="Timestamp", format="%Y-%m-%d %H:%M"),
                "Period:N",
                alt.Tooltip("BRD:Q", title="Blocking Round Duration (s)"),
            ],
        )
    )

    tab1, tab2, tab3 = st.tabs(["Trends", "Means", "Dataframe"])
    with tab1:
        st.altair_chart(chart, use_container_width=True)
    with tab2:
        morning_mean, morning_ci = mean_ci(morning_df["Morning BRD"])
        evening_mean, evening_ci = mean_ci(evening_df["Evening BRD"])

        st.write(
            f"**Morning Mean Blocking Round Duration:** {morning_mean} milliseconds"
        )
        st.write(
            f"**Evening Mean Blocking Round Duration:** {evening_mean} milliseconds"
        )
        st.write(f"**Morning Confidence Interval:** ±{morning_ci:.2f} milliseconds")
        st.write(f"**Evening Confidence Interval:** ±{evening_ci:.2f} milliseconds")

        ci_df = pd.DataFrame(
            {
                "Period": ["Morning", "Evening"],
                "Mean BRD": [morning_mean, evening_mean],
                "CI": [morning_ci, evening_ci],
            }
        )
        ci_df["Lower"] = ci_df["Mean BRD"] - ci_df["CI"]
        ci_df["Upper"] = ci_df["Mean BRD"] + ci_df["CI"]

        bars = (
            alt.Chart(ci_df)
            .mark_bar()
            .encode(
                x=alt.X("Period:N", axis=alt.Axis(title="Period")),
                y=alt.Y(
                    "Mean BRD:Q",
                    axis=alt.Axis(title="Mean Blocking Round Duration (s)"),
                ),
                tooltip=["Period", "Mean BRD", "CI"],
            )
        )

        error_bars = (
            alt.Chart(ci_df)
            .mark_errorbar(color="red", thickness=2)
            .encode(x="Period:N", y="Lower:Q", y2="Upper:Q")
        )

        chart = bars + error_bars
        st.altair_chart(chart, use_container_width=False)
    with tab3:
        st.dataframe(combined_df)


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

    # Create graph for time of day
    generate_time_of_day_chart(client_id)


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
