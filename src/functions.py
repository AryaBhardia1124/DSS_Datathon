import requests
import json
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import google.generativeai as genai

from streamlit_lottie import st_lottie
from model_utils import build_rag_context, advisor_chat 

def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            st.warning(f"Failed to load Lottie animation from URL: {url}")
            return None
        return r.json()
    except Exception as e:
        st.warning(f"Error loading Lottie from URL: {e}")
        return None

def load_lottie_file(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"Lottie file not found: {filepath}")
        return None
    except json.JSONDecodeError:
        st.warning(f"Invalid JSON in Lottie file: {filepath}")
        return None

def podium_ranking(df, student_info, top_k=5):
    if df.empty:
        st.warning("No colleges match your criteria!")
        return

    df_sorted = df.sort_values(by="score", ascending=False).head(top_k)

    medals = ["🥇", "🥈", "🥉"]
    st.subheader("🏆 Top Colleges")

    for i, row in df_sorted.reset_index(drop=True).iterrows():
        college_name = row["Institution_Name_x"]
        score = row["score"]

        if i < 3:
            st.markdown(f"{medals[i]} {college_name} — Score: {score:.2f}")
        else:
            st.markdown(f"{i+1}. {college_name} — Score: {score:.2f}")

        if st.button(f"Generate AI Summary for {college_name}", key=f"btn_{i}"):
            st.session_state.active_summary = i

        if st.session_state.active_summary == i:
            rag_context = build_rag_context(student_info, recs=[row.to_dict()])
            summary = advisor_chat(rag_context)

            with st.expander("AI Summary", expanded=True):
                st.text_area("", summary, height=300)

def rank_colleges(df, information):
    (desired_state, home_state, max_tuition, payer_status, max_debt, msi_type,
     gender, international_student, race, student_parent, major, age, estimated_income, top_k) = information

    df = df.copy()
    df = df[df["State"] == desired_state]

    if msi_type != "Any":
        df = df[df["MSI Type"] == msi_type]

    if desired_state == home_state:
        df = df[df["Average Cost of Attendance In-State"] <= max_tuition]
    else:
        df = df[df["Average Cost of Attendance Out-of-State"] <= max_tuition]

    debt_column = "Median Debt for Dependent Students" if payer_status == "Dependent" else "Median Debt for Independent Students"
    df = df[df[debt_column] <= max_debt]

    if df.empty:
        return pd.DataFrame({})

    df["score"] = 0
    weights = {
        "gender": 0.1,
        "race": 0.1,
        "major": 0.1,
        "affordability": 0.2,
        "debt": 0.2,
        "student_parent": 0.1,
        "age": 0.05,
        "earnings": 0.15
    }

    gender_col = "Percent of Women Undergraduates" if gender == "Women" else "Percent of Men Undergraduates"
    df["score"] += weights["gender"] * (df[gender_col] / 100)

    race_column_map = {
        "American Indian or Alaska Native": "Percent of American Indian or Alaska Native Undergraduates",
        "Asian": "Percent of Asian Undergraduates",
        "Black or African American": "Percent of Black or African American Undergraduates",
        "Latino": "Percent of Latino Undergraduates",
        "Native Hawaiian or Other Pacific Islander": "Percent of Native Hawaiian or Other Pacific Islander Undergraduates",
        "White": "Percent of White Undergraduates"
    }
    df["score"] += weights["race"] * (df[race_column_map[race]] / 100)

    major_column_map = {
        "Science, Technology, Engineering, and Math": "Percent of Bachelor Degrees Awarded in Science, Technology, Engineering, and Math",
        "Arts and Humanities": "Percent of Bachelor Degrees Awarded in Arts and Humanities",
        "Education": "Percent of Bachelor Degrees Awarded in Education",
        "Social Sciences": "Percent of Bachelor Degrees Awarded in Social Sciences",
        "Health Sciences": "Percent of Bachelor Degrees Awarded in Health Sciences",
        "Business": "Percent of Bachelor Degrees Awarded in Business"
    }
    df["score"] += weights["major"] * (df[major_column_map[major]] / 100)

    df["affordability_ratio"] = (estimated_income - df["Average Net Price for Low-Income Students, 2020-21"]) / estimated_income
    df["affordability_ratio"] = df["affordability_ratio"].clip(lower=0)
    df["score"] += weights["affordability"] * df["affordability_ratio"]

    df["debt_score"] = (max_debt - df[debt_column]) / max_debt
    df["debt_score"] = df["debt_score"].clip(lower=0)
    df["score"] += weights["debt"] * df["debt_score"]

    if student_parent == "Yes":
        gaps = []
        if "Student Parent Affordability Gap: Center-Based Care" in df.columns:
            gaps.append(df["Student Parent Affordability Gap: Center-Based Care"])
        if "100% TTD Student Parent Affordability Gap" in df.columns:
            gaps.append(df["100% TTD Student Parent Affordability Gap"])
        if gaps:
            combined_gap = pd.concat(gaps, axis=1).mean(axis=1)
            max_gap = combined_gap.max()
            df["student_parent_score"] = (max_gap - combined_gap) / max_gap
            df["score"] += weights["student_parent"] * df["student_parent_score"]

    df["age_score"] = df["Percent of Undergraduates Age 25 to 64"] / 100
    df["score"] += weights["age"] * df["age_score"]

    earnings_column = "Median Earnings of Independent Students Working and Not Enrolled 10 Years After Entry" \
        if payer_status == "Independent" else "Median Earnings of Dependent Students Working and Not Enrolled 10 Years After Entry"
    df["predicted_earnings"] = df[earnings_column]
    # Normalize earnings 0-1
    df["earnings_score"] = (df["predicted_earnings"] - df["predicted_earnings"].min()) / \
                           (df["predicted_earnings"].max() - df["predicted_earnings"].min() + 1e-6)
    df["score"] += weights["earnings"] * df["earnings_score"]

    df_sorted = df.sort_values(by="score", ascending=False)
    return df_sorted.head(top_k)
