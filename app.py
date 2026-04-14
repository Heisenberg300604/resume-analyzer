# =============================================================================
# app.py
# PURPOSE: The main Streamlit application entry point.
# Run with: streamlit run app.py
# =============================================================================

import streamlit as st
import plotly.graph_objects as go

# Import our custom utility functions from the utils package
from utils.pdf_extractor import extract_text_from_pdf
from utils.text_analyzer import extract_skills, match_with_jd


# =============================================================================
# PAGE CONFIGURATION
# Must be the FIRST Streamlit command in the script.
# =============================================================================
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =============================================================================
# HELPER FUNCTION: Plotly Gauge Chart
# =============================================================================
def create_gauge_chart(percentage: float) -> go.Figure:
    """
    Creates and returns a Plotly Gauge Chart for the match percentage.

    The color of the gauge needle/bar changes based on the score:
    - Red   (0–40%):  Low match
    - Orange(40–70%): Moderate match
    - Green (70–100%): Strong match

    Args:
        percentage: A float between 0 and 100.

    Returns:
        A Plotly Figure object.
    """
    # Determine bar color based on score range
    if percentage >= 70:
        bar_color = "#2ecc71"   # Green — strong match
    elif percentage >= 40:
        bar_color = "#f39c12"   # Orange — moderate match
    else:
        bar_color = "#e74c3c"   # Red — low match

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        title={
            'text': "JD Match Score",
            'font': {'size': 22, 'color': '#2c3e50'}
        },
        number={
            'suffix': "%",
            'font': {'size': 36, 'color': bar_color}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "#aab7b8"
            },
            'bar': {'color': bar_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e0e0e0",
            'steps': [
                # Background color bands on the gauge
                {'range': [0, 40],  'color': '#fde8e8'},   # Light red zone
                {'range': [40, 70], 'color': '#fef9e7'},   # Light yellow zone
                {'range': [70, 100],'color': '#eafaf1'},   # Light green zone
            ],
            'threshold': {
                'line': {'color': "#2c3e50", 'width': 4},
                'thickness': 0.75,
                'value': percentage
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        font={'family': "sans-serif"}
    )

    return fig


# =============================================================================
# MAIN APP UI
# =============================================================================

# --- Header Section ---
st.title("📄 Resume Analyzer")
st.markdown(
    """
    Upload your resume and paste a Job Description to instantly find out how well
    your skills match the role. Powered by **rule-based keyword matching** — no AI APIs needed.
    """
)
st.divider()

# --- Input Section (Two Columns Layout) ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📤 Upload Your Resume")
    uploaded_file = st.file_uploader(
        label="Choose a PDF file",
        type=["pdf"],
        help="Only PDF files are supported."
    )
    # Show a small preview confirmation when a file is uploaded
    if uploaded_file:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")

with col2:
    st.subheader("📋 Paste Job Description")
    jd_text = st.text_area(
        label="Paste the full job description here",
        height=220,
        placeholder="e.g., We are looking for a Python developer with experience in AWS, Docker, SQL..."
    )

st.divider()

# --- Analyze Button ---
# Center the button using columns
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    analyze_button = st.button(
        "🔍 Analyze Resume",
        use_container_width=True,
        type="primary"
    )


# =============================================================================
# ANALYSIS LOGIC (runs only when button is clicked)
# =============================================================================
if analyze_button:

    # --- Input Validation ---
    if not uploaded_file:
        st.error("⚠️ Please upload a resume PDF before analyzing.")
        st.stop()  # Halt execution

    if not jd_text.strip():
        st.error("⚠️ Please paste a Job Description before analyzing.")
        st.stop()  # Halt execution

    # --- Processing with a Spinner for better UX ---
    with st.spinner("⏳ Analyzing your resume... Please wait."):

        # Step 1: Extract text from the uploaded PDF
        resume_text = extract_text_from_pdf(uploaded_file)

        if not resume_text:
            st.error("❌ Could not extract text from the PDF. Please ensure it's not a scanned/image-based PDF.")
            st.stop()

        # Step 2: Extract skills from the resume text
        resume_skills = extract_skills(resume_text)

        # Step 3: Compare resume skills against the Job Description
        match_percentage, missing_skills = match_with_jd(resume_skills, jd_text)

    # --- Results Section ---
    st.divider()
    st.header("📊 Analysis Results")

    # Layout: Gauge chart on the left, skill lists on the right
    result_col1, result_col2 = st.columns([1, 1.5], gap="large")

    with result_col1:
        # Display the Plotly Gauge Chart
        gauge_fig = create_gauge_chart(match_percentage)
        st.plotly_chart(gauge_fig, use_container_width=True)

        # Add a human-readable verdict below the chart
        if match_percentage >= 70:
            st.success("🏆 **Strong Match!** Your profile aligns well with this role.")
        elif match_percentage >= 40:
            st.warning("📈 **Moderate Match.** Consider adding a few more relevant skills.")
        else:
            st.error("📉 **Low Match.** Significant skill gaps detected for this role.")

    with result_col2:
        # --- Skills Found ---
        st.subheader("✅ Skills Found in Your Resume")
        if resume_skills:
            # Display skills as neat badges using Streamlit columns
            skill_cols = st.columns(3)
            for i, skill in enumerate(resume_skills):
                with skill_cols[i % 3]:
                    st.success(f"✔ {skill.title()}")
        else:
            st.info("No recognizable skills were found in the resume.")

        st.write("")  # Spacer

        # --- Missing Skills ---
        st.subheader("❌ Skills Missing (Required by JD)")
        if missing_skills:
            miss_cols = st.columns(3)
            for i, skill in enumerate(missing_skills):
                with miss_cols[i % 3]:
                    st.error(f"✖ {skill.title()}")
        else:
            st.balloons()  # Fun celebration animation!
            st.success("🎉 Wow! Your resume covers all the skills mentioned in this Job Description.")

    # --- Summary Stats Bar ---
    st.divider()
    st.subheader("📌 Quick Summary")
    summary_c1, summary_c2, summary_c3 = st.columns(3)

    with summary_c1:
        st.metric(
            label="📄 Skills on Resume",
            value=len(resume_skills)
        )
    with summary_c2:
        st.metric(
            label="🎯 JD Match Score",
            value=f"{match_percentage}%"
        )
    with summary_c3:
        st.metric(
            label="🔧 Skills to Acquire",
            value=len(missing_skills)
        )