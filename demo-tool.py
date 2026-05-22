import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Optical Sorting Demo App",
    layout="wide"
)

title_col, logo_col = st.columns([5, 1])

with title_col:
    st.title("MV360 & 3U USA Analysis Dashboard")

with logo_col:
    try:
        st.image("assets/3U-Vision-USAdarksilhouette.png", width=200)

st.title("Optical Sorting Demo Report")

# -----------------------------
# Session State
# -----------------------------

if "passes" not in st.session_state:
    st.session_state.passes = []

if "pass_counter" not in st.session_state:
    st.session_state.pass_counter = 0


def add_pass():
    st.session_state.pass_counter += 1
    st.session_state.passes.append({
        "id": st.session_state.pass_counter,
        "name": f"Pass {st.session_state.pass_counter}",
    })


def remove_pass(pass_id):
    st.session_state.passes = [
        p for p in st.session_state.passes if p["id"] != pass_id
    ]


# -----------------------------
# Demo Info
# -----------------------------

st.header("Demo Info")

col1, col2, col3 = st.columns(3)

with col1:
    customer = st.text_input("Customer")
    product = st.text_input("Product")

with col2:
    machine = st.text_input("Machine")
    calibration = st.text_input("Calibration")

with col3:
    operator = st.text_input("Operator")
    demo_date = st.date_input("Date", value=date.today())

general_notes = st.text_area("General Demo Notes")


# -----------------------------
# Add Pass Button
# -----------------------------

st.divider()

col_a, col_b = st.columns([1, 4])

with col_a:
    st.button("Add Pass", on_click=add_pass)

if not st.session_state.passes:
    st.info("Add a pass to begin entering sorting data.")


# -----------------------------
# Pass Inputs
# -----------------------------

export_rows = []

for p in st.session_state.passes:
    pass_id = p["id"]

    with st.expander(p["name"], expanded=True):

        top1, top2, top3 = st.columns([2, 2, 1])

        with top1:
            pass_name = st.text_input(
                "Pass Name",
                value=p["name"],
                key=f"pass_name_{pass_id}"
            )

        with top2:
            pass_type = st.selectbox(
                "Pass Type",
                ["Primary", "Secondary", "Recovery", "Polish", "Custom"],
                key=f"pass_type_{pass_id}"
            )

        with top3:
            st.button(
                "Remove Pass",
                key=f"remove_{pass_id}",
                on_click=remove_pass,
                args=(pass_id,)
            )

        st.subheader("Mass Balance")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            input_weight = st.number_input(
                "Input Weight (lb)",
                min_value=0.0,
                step=0.01,
                key=f"input_weight_{pass_id}"
            )

        with c2:
            accept_weight = st.number_input(
                "Accept Weight (lb)",
                min_value=0.0,
                step=0.01,
                key=f"accept_weight_{pass_id}"
            )

        with c3:
            reject_weight = st.number_input(
                "Reject Weight (lb)",
                min_value=0.0,
                step=0.01,
                key=f"reject_weight_{pass_id}"
            )

        with c4:
            runtime_min = st.number_input(
                "Runtime (min)",
                min_value=0.0,
                step=0.1,
                key=f"runtime_{pass_id}"
            )

        total_output = accept_weight + reject_weight
        mass_balance_pct = (total_output / input_weight * 100) if input_weight else 0
        accept_yield_pct = (accept_weight / input_weight * 100) if input_weight else 0
        reject_pct = (reject_weight / input_weight * 100) if input_weight else 0
        capacity_lbs_hr = (input_weight / runtime_min * 60) if runtime_min else 0

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Mass Balance", f"{mass_balance_pct:.2f}%")
        m2.metric("Accept Yield", f"{accept_yield_pct:.2f}%")
        m3.metric("Reject %", f"{reject_pct:.2f}%")
        m4.metric("Capacity", f"{capacity_lbs_hr:.2f} lb/hr")

        st.subheader("Sample Analysis")

        tabs = st.tabs(["Input", "Accept", "Reject"])

        stream_names = ["Input", "Accept", "Reject"]

        for tab, stream in zip(tabs, stream_names):
            with tab:
                st.write(f"{stream} Stream")

                defect_rows = []

                for i in range(1, 8):
                    d1, d2 = st.columns([3, 1])

                    with d1:
                        defect_name = st.text_input(
                            f"Defect / Class {i}",
                            value="Accept" if i == 1 else "",
                            key=f"{stream}_defect_name_{pass_id}_{i}"
                        )

                    with d2:
                        defect_weight = st.number_input(
                            "Weight (g)",
                            min_value=0.0,
                            step=0.01,
                            key=f"{stream}_defect_weight_{pass_id}_{i}"
                        )

                    if defect_name or defect_weight > 0:
                        defect_rows.append({
                            "defect": defect_name,
                            "weight_g": defect_weight
                        })

                total_sample_weight = sum(row["weight_g"] for row in defect_rows)

                st.write(f"Total Sample Weight: **{total_sample_weight:.2f} g**")

                for row in defect_rows:
                    percent = (
                        row["weight_g"] / total_sample_weight * 100
                        if total_sample_weight
                        else 0
                    )

                    export_rows.append({
                        "Customer": customer,
                        "Product": product,
                        "Machine": machine,
                        "Calibration": calibration,
                        "Operator": operator,
                        "Date": demo_date,
                        "General Notes": general_notes,
                        "Pass Name": pass_name,
                        "Pass Type": pass_type,
                        "Input Weight lb": input_weight,
                        "Accept Weight lb": accept_weight,
                        "Reject Weight lb": reject_weight,
                        "Runtime min": runtime_min,
                        "Total Output lb": total_output,
                        "Mass Balance %": mass_balance_pct,
                        "Accept Yield %": accept_yield_pct,
                        "Reject %": reject_pct,
                        "Capacity lb/hr": capacity_lbs_hr,
                        "Stream": stream,
                        "Defect / Class": row["defect"],
                        "Weight g": row["weight_g"],
                        "Percent of Sample": percent,
                    })

        pass_notes = st.text_area(
            "Pass Notes",
            key=f"pass_notes_{pass_id}"
        )

        for row in export_rows:
            if row["Pass Name"] == pass_name:
                row["Pass Notes"] = pass_notes


# -----------------------------
# Summary + Download
# -----------------------------

st.divider()
st.header("Export Summary")

df = pd.DataFrame(export_rows)

if not df.empty:
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Full Demo CSV",
        data=csv,
        file_name="optical_sorting_demo_report.csv",
        mime="text/csv"
    )
else:
    st.warning("No data entered yet.")