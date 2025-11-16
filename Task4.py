import streamlit as st

st.set_page_config(page_title="BMI Calculator", page_icon="🏋️")

st.title("🏋️ BMI Calculator")

# Inputs
height = st.number_input("Enter your height (cm)", min_value=50.0, max_value=250.0, step=0.1)
weight = st.number_input("Enter your weight (kg)", min_value=10.0, max_value=300.0, step=0.1)

if st.button("Calculate BMI"):

    if height > 0 and weight > 0:

        # Convert height to meters
        height_m = height / 100

        # BMI formula
        bmi = weight / (height_m ** 2)

        # Determine category
        if bmi < 18.5:
            category = "Underweight"
            color = "#ADD8E6"  # light blue
        elif 18.5 <= bmi < 24.9:
            category = "Normal Weight"
            color = "#90EE90"  # light green
        elif 25 <= bmi < 29.9:
            category = "Overweight"
            color = "#FFD580"  # light orange
        else:
            category = "Obese"
            color = "#FF7F7F"  # light red

        # Display result
        st.markdown(
            f"""
            <div style='padding:20px; border-radius:10px; background-color:{color}; text-align:center;'>
                <h2>Your BMI: {bmi:.2f}</h2>
                <h3>Category: {category}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("Please enter valid height and weight values.")
