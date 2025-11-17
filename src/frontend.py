# streamlit_app.py
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

from streamlit_lottie import st_lottie
from model_utils import build_rag_context, advisor_chat
from functions import load_lottie_url, load_lottie_file, podium_ranking, rank_colleges

if "ranked_df" not in st.session_state:
    st.session_state.ranked_df = None

if "active_summary" not in st.session_state:
    st.session_state.active_summary = None

lottie_college = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tno6cg2w.json")

if lottie_college:
    st_lottie(lottie_college, height=200)
else:
    st.info("No animation to display.")

college_df = pd.read_csv("../data/Joint_Data.csv")
college_df.rename(columns = {'Institution Name_x':'Institution_Name_x'}, inplace = True)
college_df = college_df.drop_duplicates(subset=["Institution_Name_x"])

st.set_page_config(page_title = "College Fit Predictor", page_icon = "🎓")

st.title(f"🎓 College Recommendation Tool")
st.write("Input your preferences to find colleges that best match your needs.")
st.header("Preferences")

all_states = sorted(college_df['State'].unique())
desired_state = st.selectbox("Desired State", ["Any"] + all_states)
home_state = st.selectbox("Home State", all_states)

if desired_state == home_state:
    min_tuition = college_df["Average Cost of Attendance In-State"].min()
else:
    min_tuition = college_df["Average Cost of Attendance Out-of-State"].min()

max_tuition = st.number_input(f"Maximum Tuition/Payment (>= {int(min_tuition)})",
                              min_value = int(min_tuition),
                              step = 1000)

payer_status = st.selectbox("Are you an Independent or Dependent Student?", ["Independent", "Dependent"])

if payer_status == "Independent":
    min_debt = college_df["Median Debt for Independent Students"].min()
else:
    min_debt = college_df["Median Debt for Dependent Students"].min()

max_debt = st.number_input(f"Maximum Acceptable Debt (>= {int(min_debt)})",
                            min_value = int(min_debt),
                            step = 1000)

msi_list = college_df["MSI Type"].unique().tolist()
msi_list.append("Any")
msi_type = st.selectbox("What type of Minority-Serving Institution do you want to go to?", msi_list)



st.header("Personal Inquiry")

gender = st.selectbox("Gender", ["Women", "Men"])

international_student = st.selectbox("International Student?", ["Yes", "No"])

race = st.selectbox("Race", ["American Indian or Alaska Native", 
                             "Asian", 
                             "Black or African American", 
                             "Latino", 
                             "Native Hawaiian or Other Pacific Islander", 
                             "White"])

student_parent = st.selectbox("Are you a student parent?", ["Yes", "No"])

major = st.selectbox("Desired Field of Study", ["Science, Technology, Engineering, and Math", 
                                                "Arts and Humanities",
                                                "Education",
                                                "Social Sciences",
                                                "Health Sciences",
                                                "Business"])

age = st.number_input("Age", min_value = 0, step = 1)

estimated_income = st.number_input("Estimated Annual Income", 
                                min_value = 0, 
                                step = 1000)

top_k = st.number_input("Number of Ranked Colleges to Display",
                        min_value = 1,
                        max_value = 10)

information = []
information.append(desired_state)
information.append(home_state)
information.append(max_tuition)
information.append(payer_status)
information.append(max_debt)
information.append(msi_type)
information.append(gender)
information.append(international_student)
information.append(race)
information.append(student_parent)
information.append(major)
information.append(age)
information.append(estimated_income)
information.append(top_k)

student_info = {
    "Desired State": desired_state,
    "Home State": home_state,
    "Max Tuition": max_tuition,
    "Payer Status": payer_status,
    "Max Debt": max_debt,
    "MSI Type": msi_type,
    "Gender": gender,
    "International Student": international_student,
    "Race": race,
    "Student Parent": student_parent,
    "Major": major,
    "Age": age,
    "Estimated Income": estimated_income,
    "Top K Colleges": top_k
}

if st.button("Find Colleges"):
    st.session_state.ranked_df = rank_colleges(college_df, information)
    st.session_state.active_summary = None  # clear AI summary selection

if st.session_state.ranked_df is not None:
    podium_ranking(
        st.session_state.ranked_df,
        student_info=student_info,
        top_k=top_k
    )