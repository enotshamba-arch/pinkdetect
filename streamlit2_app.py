import streamlit as st
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Pink Sequence Detector", page_icon="🚀")
TARGET_MINUTES = [1, 10, 21, 34, 41, 56] # Common community slots

# Initialize History in Session (Preserves data on refresh)
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🚀 Pink Round Detector")
st.subheader("Time-Based & Sequence Analysis")

# --- USER INPUT SECTION ---
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        mult = st.number_input("Enter Multiplier (e.g. 1.45)", min_value=1.0, step=0.1)
    with col2:
        time_str = st.text_input("Round Time (HH:MM:SS)", datetime.now().strftime("%H:%M:%S"))
    
    submit = st.form_submit_button("Add Round to History")
    if submit:
        st.session_state.history.append({"mult": mult, "time": time_str})

# --- ANALYSIS LOGIC ---
if st.session_state.history:
    data = st.session_state.history
    now = datetime.now()
    curr_min = now.minute
    
    # 1. Blue Streak & Feeder Detection
    recent_mults = [r["mult"] for r in data[-4:]]
    blue_streak = sum(1 for m in recent_mults if m < 2.0)
    has_feeder = any(4.0 <= m < 10.0 for m in recent_mults)
    
    # 2. Timing Window Detection
    pinks = [r for r in data if r["mult"] >= 10.0]
    in_time_window = False
    if pinks:
        lp_time = datetime.strptime(pinks[-1]["time"], "%H:%M:%S").replace(
            year=now.year, month=now.month, day=now.day)
        mins_since = (now - lp_time).total_seconds() / 60
        in_time_window = (4.0 <= mins_since <= 6.0) or (9.0 <= mins_since <= 12.0)

    in_hourly_slot = curr_min in TARGET_MINUTES

    # --- DISPLAY SIGNALS ---
    st.divider()
    if has_feeder and (in_time_window or in_hourly_slot) and blue_streak >= 1:
        st.error("🔥 CRITICAL SIGNAL: PINK IMMINENT. Feeder + Time + Streak Aligned.")
    elif has_feeder:
        st.warning(f"⚡ FEEDER DETECTED ({recent_mults[-1]}x). Algorithm warming up. Wait for next minute slot.")
    elif blue_streak >= 3:
        st.info(f"🕒 RECOVERY MODE: {blue_streak} Blues detected. Watching for Feeder or Pink.")
    else:
        st.success("📡 SCANNING: Waiting for pattern alignment...")

    # Display History Table
    st.write("### Recent History")
    st.table(data[::-1]) # Show latest on top
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
