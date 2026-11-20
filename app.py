import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from database import init_db, add_patient, get_patients, update_status, get_counts
from predictor import predict_wait

st.set_page_config(
    page_title="MediQueue AI | Smart Hospital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
init_db()

st.title("🏥 MediQueue AI")
st.caption("Smart Hospital Queue & Appointment Management")

st.warning(
    "DEMO VERSION: This app is for education and demonstration. "
    "Do not enter real patient-identifying or medical information. "
    "Clinical triage and emergency decisions must always be made by qualified staff."
)

DEPARTMENTS = [
    "General Consultation", "Paediatrics", "Maternity",
    "Dental", "Laboratory", "Pharmacy"
]

page = st.sidebar.radio(
    "Hospital menu",
    ["Dashboard", "Register Patient", "Manage Queue", "Appointments"]
)

if page == "Dashboard":
    st.subheader("Hospital Dashboard")
    counts = get_counts()
    a, b, c = st.columns(3)
    a.metric("Patients waiting", counts.get("Waiting", 0))
    b.metric("Currently in service", counts.get("In service", 0))
    c.metric("Completed visits", counts.get("Completed", 0))

    dept = st.selectbox("View department", ["All"] + DEPARTMENTS)
    waiting = get_patients(status="Waiting", department=dept)
    if waiting:
        table = []
        for p in waiting:
            prediction = predict_wait(p["id"])
            table.append({
                "Queue number": f"MQ-{p['id']:04d}",
                "Patient": p["patient_name"],
                "Department": p["department"],
                "Priority": p["priority"],
                "Appointment": p["appointment_time"].replace("T", " "),
                "People ahead": prediction["people_ahead"] if prediction else 0,
                "Estimated wait (min)": prediction["minutes"] if prediction else 0
            })
        st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
    else:
        st.success("No patients are currently waiting.")

elif page == "Register Patient":
    st.subheader("Register a Patient")
    with st.form("register_patient", clear_on_submit=True):
        name = st.text_input("Patient name *")
        phone = st.text_input("Phone number (optional)")
        department = st.selectbox("Department", DEPARTMENTS)
        appointment_day = st.date_input("Appointment date", value=date.today())
        appointment_clock = st.time_input("Appointment time", value=time(9, 0))
        priority = st.selectbox(
            "Priority (assigned by authorized clinical staff)",
            ["Normal", "Urgent", "Emergency"]
        )
        submitted = st.form_submit_button("Register patient", type="primary")

    if submitted:
        if not name.strip():
            st.error("Please enter a patient name.")
        else:
            appointment = datetime.combine(appointment_day, appointment_clock)
            number = add_patient(name, phone, department, appointment, priority)
            st.success(f"Patient registered! Queue number: MQ-{number:04d}")

elif page == "Manage Queue":
    st.subheader("Manage Patient Queue")
    dept = st.selectbox("Department filter", ["All"] + DEPARTMENTS)
    patients = get_patients(department=dept)

    if not patients:
        st.info("No patient records yet.")
    for p in patients:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.markdown(f"**MQ-{p['id']:04d} — {p['patient_name']}**")
            col1.write(f"{p['department']} · {p['priority']}")
            col2.write(f"Status: **{p['status']}**")
            if p["status"] == "Waiting":
                estimate = predict_wait(p["id"])
                if estimate:
                    col2.write(f"Estimated wait: **{estimate['minutes']} min**")
                if col3.button("Start service", key=f"start_{p['id']}"):
                    update_status(p["id"], "In service")
                    st.rerun()
            elif p["status"] == "In service":
                duration = col3.number_input(
                    "Service minutes", min_value=1, max_value=300,
                    value=15, key=f"duration_{p['id']}"
                )
                if col3.button("Complete visit", key=f"complete_{p['id']}"):
                    update_status(p["id"], "Completed", duration)
                    st.rerun()
            else:
                col3.success("Completed")

elif page == "Appointments":
    st.subheader("Appointment Schedule")
    selected_day = st.date_input("Select date", value=date.today())
    records = get_patients()
    matches = [
        p for p in records
        if datetime.fromisoformat(p["appointment_time"]).date() == selected_day
    ]
    if matches:
        df = pd.DataFrame([{
            "Queue number": f"MQ-{p['id']:04d}",
            "Patient": p["patient_name"],
            "Department": p["department"],
            "Time": datetime.fromisoformat(p["appointment_time"]).strftime("%H:%M"),
            "Priority": p["priority"],
            "Status": p["status"]
        } for p in matches])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No appointments scheduled for this date.")

st.sidebar.divider()
st.sidebar.caption("MediQueue AI · GitHub deployment demo")
