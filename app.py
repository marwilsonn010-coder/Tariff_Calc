# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Tariff Savings Calculator", layout="centered")

st.title("Tariff Savings Calculator")

# --- Inputs ---
material = st.selectbox("Material", ["uPVC", "Aluminum"])
order_value = st.number_input("Order value (USD)", min_value=0.0, step=100.0, value=10000.0, format="%.2f")

st.subheader("Flat Fees per Origin (USD)")
st.caption("HMF and MPF are editable flat fees. Defaults are 0.")

origins = ["Bahrain", "China", "Poland", "Mexico"]

# Fee inputs
fees = {}
for o in origins:
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown(f"**{o}**")
    with c2:
        hmf = st.number_input(f"HMF — {o}", key=f"hmf_{o}", min_value=0.0, step=10.0, value=0.0)
    with c3:
        mpf = st.number_input(f"MPF — {o}", key=f"mpf_{o}", min_value=0.0, step=10.0, value=0.0)
    fees[o] = {"HMF": hmf, "MPF": mpf}

# --- Duty rates ---
rates = {
    "uPVC":   {"Bahrain": 0.10, "China": 0.748, "Poland": 0.4724, "Mexico": 0.5030},
    "Aluminum":{"Bahrain": 0.10, "China": 0.752, "Poland": 0.4765, "Mexico": 0.5070},
}

# --- Compute table ---
rows = []
for origin in origins:
    duty_rate = rates[material][origin]
    duty_amount = order_value * duty_rate
    hmf = fees[origin]["HMF"]
    mpf = fees[origin]["MPF"]
    total = order_value + duty_amount + hmf + mpf
    rows.append({
        "Origin": origin,
        "Duty rate": duty_rate,
        "Order value": order_value,
        "Duty amount": duty_amount,
        "HMF": hmf,
        "MPF": mpf,
        "Total": total
    })

df = pd.DataFrame(rows).sort_values("Total", ascending=True, ignore_index=True)

# Savings vs next
totals = df["Total"].values
savings_next = []
for i in range(len(df)):
    if i < len(df) - 1:
        savings_next.append(totals[i+1] - totals[i])
    else:
        savings_next.append(np.nan)
df["Savings vs next"] = savings_next

# Best option
best_idx = df["Total"].idxmin()
df["Best option"] = ["✅" if i == best_idx else "" for i in df.index]

# Display summary
best_row = df.loc[best_idx]
st.success(
    f"🏆 Best option: **{best_row['Origin']}** — Total **${best_row['Total']:,.2f}**"
    + (f" | Saves **${df.loc[0, 'Savings vs next']:,.2f}** vs next option" if pd.notna(df.loc[0, 'Savings vs next']) else "")
)

# Reorder columns
df = df[["Best option","Origin","Duty rate","Order value","Duty amount","HMF","MPF","Total","Savings vs next"]]

# Format numbers
fmt = {
    "Duty rate": "{:.2%}",
    "Order value": "${:,.2f}",
    "Duty amount": "${:,.2f}",
    "HMF": "${:,.2f}",
    "MPF": "${:,.2f}",
    "Total": "${:,.2f}",
    "Savings vs next": "${:,.2f}",
}

# Highlight best option (with dark text)
def highlight_best(_df: pd.DataFrame):
    styles = pd.DataFrame("", index=_df.index, columns=_df.columns)
    styles.loc[best_idx, :] = "background-color:#B9F6CA; color:black; font-weight:bold;"  # green highlight, black text
    return styles

styled = df.style.format(fmt).apply(highlight_best, axis=None)
st.dataframe(styled, use_container_width=True)

# Download CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv, file_name="tariff_savings.csv", mime="text/csv")

st.caption("Duty = rate × order value; Total = order + duty + HMF + MPF.")
