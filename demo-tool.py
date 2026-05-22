import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="3U USA Demo Tool",
    layout="wide"
)

title_col, logo_col = st.columns([5, 1])

with title_col:
    st.title("3U USA Demo Toolv1")

with logo_col:
    st.image("assets/3U-Vision-USAdarksilhouette.png", width=200)

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

def calculate_yield(input_flow, gi_pct, ga_pct, gr_pct):
    Gi = gi_pct / 100
    Ga = ga_pct / 100
    Gr = gr_pct / 100

    if input_flow <= 0:
        return None

    if Gi <= 0:
        return None

    if Ga == Gr:
        return None

    accept_flow = input_flow * ((Gi - Gr) / (Ga - Gr))
    reject_flow = input_flow * ((Ga - Gi) / (Ga - Gr))

    good_in_input = Gi * input_flow
    good_in_accept = Ga * accept_flow
    good_lost_to_reject = Gr * reject_flow

    yield_pct = (good_in_accept / good_in_input) * 100
    loss_pct = (good_lost_to_reject / good_in_input) * 100

    return {
        "accept_flow": accept_flow,
        "reject_flow": reject_flow,
        "good_in_input": good_in_input,
        "good_in_accept": good_in_accept,
        "good_lost_to_reject": good_lost_to_reject,
        "yield_pct": yield_pct,
        "loss_pct": loss_pct,
    }
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
            input_weight = st.number_input("Input Weight (g)", min_value=0.0, step=0.01, key=f"input_weight_{pass_id}")
        with c2:
            accept_weight = st.number_input("Accept Weight (g)", min_value=0.0, step=0.01, key=f"accept_weight_{pass_id}")
        with c3:
            reject_weight = st.number_input("Reject Weight (g)", min_value=0.0, step=0.01, key=f"reject_weight_{pass_id}")
        with c4:
            runtime_sec = st.number_input("Runtime (sec)", min_value=0.0, step=0.1, key=f"runtime_{pass_id}")

        total_output = accept_weight + reject_weight
        mass_balance_pct = (total_output / input_weight * 100) if input_weight else 0
        accept_stream_yield_pct = (accept_weight / input_weight * 100) if input_weight else 0
        reject_stream_pct = (reject_weight / input_weight * 100) if input_weight else 0
        throughput_lbs_hr = ((input_weight * 0.00220462) / runtime_sec * 3600) if runtime_sec else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Mass Balance", f"{mass_balance_pct:.2f}%")
        m2.metric("Accept Stream Yield", f"{accept_stream_yield_pct:.2f}%")
        m3.metric("Reject Stream %", f"{reject_stream_pct:.2f}%")
        m4.metric("Throughput", f"{throughput_lbs_hr:,.2f} lb/hr")

        st.subheader("Sample Analysis")

        tabs = st.tabs(["Input", "Accept", "Reject"])
        stream_names = ["Input", "Accept", "Reject"]
        stream_summaries = {}

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

                good_sample_weight = sum(
                    row["weight_g"]
                    for row in defect_rows
                    if row["defect"].strip().lower() == "accept"
                )

                defect_sample_weight = total_sample_weight - good_sample_weight

                good_pct = (
                    good_sample_weight / total_sample_weight * 100
                    if total_sample_weight
                    else 0
                )

                defect_pct = 100 - good_pct if total_sample_weight else 0

                stream_summaries[stream] = {
                    "total_sample_weight": total_sample_weight,
                    "good_pct": good_pct,
                    "defect_pct": defect_pct
                }

                st.write(f"Total Sample Weight: **{total_sample_weight:.2f} g**")
                st.write(f"Good Product %: **{good_pct:.2f}%**")
                st.write(f"Defect Product %: **{defect_pct:.2f}%**")

                for row in defect_rows:
                    percent = (
                        row["weight_g"] / total_sample_weight * 100
                        if total_sample_weight
                        else 0
                    )


        # -----------------------------
"Pass Notes": pass_notes,
})

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