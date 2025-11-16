import streamlit as st

st.title("Simple User Form")

# Create a form container
with st.form("user_form"):
    name = st.text_input("Enter your name")
    age = st.slider("Select your age", min_value=1, max_value=100, value=25)

    # Submit button
    submitted = st.form_submit_button("Submit")

# When the submit button is pressed
if submitted:
    st.success(f"Hello, {name}! You are {age} years old 🎉")
