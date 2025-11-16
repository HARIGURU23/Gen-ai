import streamlit as st

st.set_page_config(page_title="Simple Calculator", page_icon="🧮")

st.title("🧮 Simple Calculator")

# --- Inputs ---
num1 = st.number_input("Enter first number:", value=0.0)
num2 = st.number_input("Enter second number:", value=0.0)

operation = st.selectbox(
    "Select Operation:",
    ["Add (+)", "Subtract (-)", "Multiply (×)", "Divide (÷)"]
)

# --- Calculator Logic ---
def calculate(n1, n2, op):
    if op == "Add (+)":
        return n1 + n2
    elif op == "Subtract (-)":
        return n1 - n2
    elif op == "Multiply (×)":
        return n1 * n2
    elif op == "Divide (÷)":
        return "Error: Cannot divide by zero" if n2 == 0 else n1 / n2

result = calculate(num1, num2, operation)

# --- Output (Instant Result) ---
st.success(f"Result: {result}")
