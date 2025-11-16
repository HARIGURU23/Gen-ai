import streamlit as st
import pandas as pd

st.title("💰 Expense Splitter App")
st.write("Split expenses among friends for trips, dinner, or outings.")

# --- Input Section ---
st.header("Enter Expense Details")

total_amount = st.number_input("Total Expense Amount (₹)", min_value=0.0, step=0.1)
num_people = st.number_input("Number of Friends", min_value=1, step=1)

st.write("### Enter Names and Contributions")
names = []
contributions = []

for i in range(int(num_people)):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"Name of Person {i+1}", key=f"name_{i}")
        names.append(name if name else f"Person {i+1}")
    with col2:
        paid = st.number_input(f"Amount paid by {names[i]}", min_value=0.0, step=0.1, key=f"paid_{i}")
        contributions.append(paid)

# --- Calculation ---
if st.button("Calculate Split"):
    total_paid = sum(contributions)

    if total_amount == 0:
        st.error("Please enter a valid total amount!")
    elif total_paid != total_amount:
        st.warning(f"⚠️ The total contributions ({total_paid}) do not match the total expense ({total_amount}).")
    else:
        per_person_share = total_amount / num_people
        st.success(f"Each person must pay: ₹{per_person_share:.2f}")

        # Calculate balance for each person
        balance = [paid - per_person_share for paid in contributions]

        df = pd.DataFrame({
            "Name": names,
            "Paid": contributions,
            "Balance (positive = gets back)": balance
        })

        st.write("### 💸 Settlement Overview")
        st.dataframe(df)

        st.write("### 🔍 Who Pays Who?")

        # Determine who owes and who gets
        owes = []
        gets = []

        for i in range(num_people):
            if balance[i] < 0:
                owes.append([names[i], -balance[i]])
            elif balance[i] > 0:
                gets.append([names[i], balance[i]])

        # Settlement Logic
        settlement = []
        i = j = 0
        while i < len(owes) and j < len(gets):
            owe_name, owe_amt = owes[i]
            get_name, get_amt = gets[j]

            amount = min(owe_amt, get_amt)
            settlement.append(f"➡️ **{owe_name} pays ₹{amount:.2f} to {get_name}**")

            owes[i][1] -= amount
            gets[j][1] -= amount

            if owes[i][1] == 0:
                i += 1
            if gets[j][1] == 0:
                j += 1

        for line in settlement:
            st.write(line)

        if not settlement:
            st.info("Everyone is settled. No payments needed! 🎉")
