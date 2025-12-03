import streamlit as st
import pandas as pd

EXCEL_FILE = "Apartment_Progress_Weighted-Progress_App_ITowerAvg_AppView_v5.xlsx"
SHEET_NAME = "Apartment Progress"

# Activity columns and weights (same as Excel row 2)
ACTIVITY_COLS = [
    "MEP Work",
    "Ceiling",
    "Tile Work",
    "Paint Work",
    "Aluminum Work",
    "Wood Work",
    "MEP Fixtures",
    "MS Work",
    "External Plaster",
    "External Travertine",
    "External Paint",
    "Cleaning",
]

WEIGHTS = {
    "MEP Work": 0.10,
    "Ceiling": 0.15,
    "Tile Work": 0.20,
    "Paint Work": 0.10,
    "Aluminum Work": 0.10,
    "Wood Work": 0.20,
    "MEP Fixtures": 0.05,
    "MS Work": 0.02,
    "External Plaster": 0.03,
    "External Travertine": 0.02,
    "External Paint": 0.03,
    "Cleaning": 0.02,
}

@st.cache_data
def load_data():
    # Read sheet
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, engine="openpyxl")
    # Keep only real apartments (where Apartment No is numeric)
    df = df[pd.to_numeric(df["Apartment No"], errors="coerce").notna()].copy()
    df["Apartment No"] = df["Apartment No"].astype(int)

    # Some people store 0–1, some 0–100; normalize to 0–1
    for col in ACTIVITY_COLS:
        # If any value > 1, we assume 0–100 and divide
        if (df[col] > 1).any():
            df[col] = df[col] / 100.0

    return df

df = load_data()

# ---- UI ----
st.title("I-Tower Apartment Progress Viewer")

min_apt = int(df["Apartment No"].min())
max_apt = int(df["Apartment No"].max())

apt_no = st.number_input(
    "Enter Apartment No:",
    min_value=min_apt,
    max_value=max_apt,
    step=1,
    value=min_apt,
)

row = df[df["Apartment No"] == apt_no]

if row.empty:
    st.error("Apartment not found in data.")
else:
    row = row.iloc[0]

    # Compute overall for apartment using weights
    apt_overall = sum(row[col] * WEIGHTS[col] for col in ACTIVITY_COLS)

    # Compute I-Tower averages (same logic as your Excel I-Tower row)
    tower_means = df[ACTIVITY_COLS].mean()
    tower_overall = sum(tower_means[col] * WEIGHTS[col] for col in ACTIVITY_COLS)

    # ---- Top summary ----
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Apartment No", f"{int(row['Apartment No'])}")
        st.write(f"Floor: **{row['Floor']}**")
    with c2:
        st.metric("Apartment Total Progress", f"{apt_overall*100:.1f}%")
    with c3:
        st.metric("I-Tower Overall Progress", f"{tower_overall*100:.1f}%")

    st.markdown("---")

    # ---- Activity table ----
    table = []
    for act in ACTIVITY_COLS:
        table.append({
            "Activity": act,
            "Apartment Progress": f"{row[act]*100:.1f}%",
            "I-Tower Avg": f"{tower_means[act]*100:.1f}%",
        })

    st.subheader("Activity-wise Comparison")
    st.table(pd.DataFrame(table))
