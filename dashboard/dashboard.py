import streamlit as st
import pandas as pd
import altair as alt
import httpx
import os

# API endpoint configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="SOC Operations Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ SOC Operations Center - Interactive Triage Game")

# 1. Initialize session state variables for tracking player scores and history
if "score" not in st.session_state:
    st.session_state.score = 0
if "total_triaged" not in st.session_state:
    st.session_state.total_triaged = 0
if "correct_decisions" not in st.session_state:
    st.session_state.correct_decisions = 0
if "accuracy_history" not in st.session_state:
    st.session_state.accuracy_history = []  # Stores historical accuracy for the line chart

def fetch_alerts():
    """Fetch all alerts from the FastAPI engine."""
    try:
        response = httpx.get(f"{API_URL}/alerts", timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Cannot reach API: {e}")
    return []

def evaluate_triage(alert_id, user_choice, is_malicious):
    """Evaluate user triage decision against ground truth and update backend status."""
    actual_is_threat = is_malicious
    user_thought_threat = (user_choice == "TRUE_POSITIVE")
    
    is_correct = (user_thought_threat == actual_is_threat)
    
    try:
        response = httpx.patch(f"{API_URL}/alerts/{alert_id}", json={"value": user_choice}, timeout=5.0)
        if response.status_code == 200:
            st.session_state.total_triaged += 1
            if is_correct:
                st.session_state.correct_decisions += 1
                st.success("Correct decision! Accuracy updated.")
            else:
                st.error("Incorrect decision! That was a misclassification.")
            
            # Calculate and save accuracy history for the trend curve
            current_acc = (st.session_state.correct_decisions / st.session_state.total_triaged) * 100
            st.session_state.accuracy_history.append({
                "triage_step": st.session_state.total_triaged,
                "accuracy": current_acc
            })
            
            st.rerun()
        else:
            st.error(f"Failed to update alert status: {response.text}")
    except Exception as e:
        st.error(f"API connection error during patch: {e}")

# Fetch data and convert to DataFrame
alerts = fetch_alerts()
df = pd.DataFrame(alerts)

# 2. Display key performance metrics at the top
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Triaged", st.session_state.total_triaged)
with col2:
    accuracy = (st.session_state.correct_decisions / st.session_state.total_triaged * 100) if st.session_state.total_triaged > 0 else 0
    st.metric("Accuracy", f"{accuracy:.1f}%")
with col3:
    pending_count = len(df[df["status"] == "PENDING"]) if not df.empty and "status" in df.columns else 0
    st.metric("Pending Alerts", pending_count)

st.divider()

# 3. TOP ANALYTICS & CHARTS SECTION (Status breakdown & Accuracy progression curve)
if not df.empty and "status" in df.columns:
    st.subheader("📊 SOC Performance & Operations Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**Alert Status Breakdown**")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        
        # Colored bar chart (Yellow for PENDING, Red for TRUE_POSITIVE, Green for FALSE_POSITIVE)
        status_chart = alt.Chart(status_counts).mark_bar().encode(
            x=alt.X('status:N', sort=None, title="Status"),
            y=alt.Y('count:Q', title="Count"),
            color=alt.Color('status:N', scale=alt.Scale(
                domain=['PENDING', 'TRUE_POSITIVE', 'FALSE_POSITIVE'],
                range=['#f39c12', '#e74c3c', '#2ecc71'] # Yellow, Red, Green
            ), legend=None)
        ).properties(height=250)
        st.altair_chart(status_chart, use_container_width=True)
        
    with chart_col2:
        st.markdown("**Accuracy Progression Over Time (%)**")
        if st.session_state.accuracy_history:
            acc_df = pd.DataFrame(st.session_state.accuracy_history)
            
            # Line chart showing accuracy evolution
            acc_chart = alt.Chart(acc_df).mark_line(
                point=alt.OverlayMarkDef(color="blue", size=60),
                color="#3498db",
                strokeWidth=3
            ).encode(
                x=alt.X('triage_step:Q', title="Triaged Count"),
                y=alt.Y('accuracy:Q', scale=alt.Scale(domain=[0, 100]), title="Accuracy (%)")
            ).properties(height=250)
            st.altair_chart(acc_chart, use_container_width=True)
        else:
            st.info("Start triaging alerts below to generate your accuracy progression curve.")

st.divider()

# 4. ACTIVE TRIAGE SECTION
if df.empty:
    st.info("Waiting for incoming alerts from the log generator...")
else:
    pending_df = df[df["status"] == "PENDING"] if "status" in df.columns else pd.DataFrame()
    
    if pending_df.empty:
        st.success("All caught up! No pending alerts to triage. Great job SOC Analyst!")
        with st.expander("View All Processed Alerts History"):
            st.dataframe(df)
    else:
        st.subheader("⚠️ Alert Triage Queue")
        
        alert_options = pending_df.apply(lambda row: f"ID {row['id']} - {row['event_type']} ({row['ip_source']})", axis=1).tolist()
        selected_option = st.selectbox("Select an alert to investigate:", alert_options)
        
        if selected_option:
            selected_id = int(selected_option.split(" ")[1])
            alert_data = pending_df[pending_df["id"] == selected_id].iloc[0]
            
            st.markdown(f"**Event Type:** {alert_data['event_type']}")
            st.markdown(f"**Source IP:** `{alert_data['ip_source']}`")
            st.markdown(f"**Risk Score:** `{alert_data['score']}/10`")
            st.info(f"**Message:** {alert_data['message']}")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🚨 Confirm Threat (True Positive)", type="primary"):
                    evaluate_triage(selected_id, "TRUE_POSITIVE", alert_data["is_malicious"])
            
            with col_btn2:
                if st.button("✅ Dismiss Alert (False Positive)", type="secondary"):
                    evaluate_triage(selected_id, "FALSE_POSITIVE", alert_data["is_malicious"])