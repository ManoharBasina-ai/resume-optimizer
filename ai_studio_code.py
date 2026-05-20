import streamlit as st
import openai
import pypdf
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Resume Score & ATS Optimizer | Naukri Style",
    page_icon="💼",
    layout="wide"
)

# --- NAUKRI AESTHETIC CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f4f7fa; }

    /* Header Simulation */
    .nav-bar {
        background-color: #ffffff;
        padding: 10px 60px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e6e6e6;
        margin-bottom: 25px;
    }
    .naukri-logo {
        color: #457eff;
        font-size: 26px;
        font-weight: 800;
        font-family: 'Roboto', sans-serif;
    }

    /* Card Styling */
    .naukri-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #457eff;
        color: white;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #270b5d;
        color: white;
        transform: translateY(-2px);
    }

    /* Score Badge */
    .score-container {
        text-align: center;
        padding: 20px;
    }
    .score-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: #f0faff;
        border: 4px solid #457eff;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: bold;
        color: #457eff;
    }

    /* Typography */
    h1, h2, h3 { color: #270b5d; font-family: 'Roboto', sans-serif; }
    .label-text { color: #666; font-size: 14px; margin-bottom: 10px; }
    </style>
    
    <div class="nav-bar">
        <div class="naukri-logo">naukri <span style="color:#333">optimizer</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def get_ai_analysis(resume_text, jd_text, api_key):
    client = openai.OpenAI(api_key=api_key)
    
    # This prompt handles the scoring, gap analysis, and the 95+ rewrite logic
    prompt = f"""
    Act as a Senior Technical Recruiter and ATS Expert.
    
    INPUTS:
    Resume: {resume_text}
    Job Description: {jd_text}
    
    TASK:
    1. Rate the current resume against the JD (0-100).
    2. Identify missing keywords and skills.
    3. Rewrite the resume to achieve a score of at least 95/100.
    
    REWRITING RULES:
    - Use a clean, single-column, text-based format.
    - Use standard headers: PROFESSIONAL SUMMARY, WORK EXPERIENCE, SKILLS, EDUCATION.
    - Use the 'Action Verb + Task + Result' formula for bullet points.
    - Naturally integrate all high-priority keywords from the JD.
    - If information is missing to reach 95%, use the existing info to maximize the score, but add a section at the end called 'RECOMMENDED ADDITIONS' listing what the user should add to hit the 95+ mark.

    OUTPUT FORMAT (Strictly follow this):
    ---SCORE---
    [Number only]
    ---GAPS---
    [List of missing skills/keywords]
    ---REWRITTEN---
    [The full rewritten resume]
    ---ADDITIONS---
    [What is needed to reach 95+ if not already there]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an expert resume writer."},
                  {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- MAIN UI ---
st.markdown("<h1 style='text-align: center;'>Step up your career with AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-bottom: 40px;'>Analyze your resume match and get an ATS-optimized version in seconds.</p>", unsafe_allow_html=True)

# Sidebar for API Key
with st.sidebar:
    st.image("https://static.naukimg.com/s/4/100/i/naukri_Logo.png", width=140)
    st.markdown("### Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password", help="Get your key from platform.openai.com")
    st.info("Your data is processed securely and not stored.")

# Input Section
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="naukri-card">', unsafe_allow_html=True)
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload your PDF resume", type="pdf", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="naukri-card">', unsafe_allow_html=True)
    st.subheader("🎯 Job Description")
    jd_text = st.text_area("Paste the job description here", height=150, label_visibility="collapsed", placeholder="Paste the JD here...")
    st.markdown('</div>', unsafe_allow_html=True)

# Action Button
if st.button("Analyze & Optimize for 95+ Score"):
    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not uploaded_file or not jd_text:
        st.warning("Please provide both your resume and the job description.")
    else:
        with st.spinner("AI is analyzing and rewriting your resume..."):
            resume_content = extract_text_from_pdf(uploaded_file)
            raw_result = get_ai_analysis(resume_content, jd_text, api_key)
            
            # Parsing the AI response
            try:
                parts = raw_result.split("---")
                score = "0"
                gaps = ""
                rewritten = ""
                additions = ""
                
                for part in parts:
                    if "SCORE" in part: score = part.replace("SCORE", "").strip()
                    if "GAPS" in part: gaps = part.replace("GAPS", "").strip()
                    if "REWRITTEN" in part: rewritten = part.replace("REWRITTEN", "").strip()
                    if "ADDITIONS" in part: additions = part.replace("ADDITIONS", "").strip()

                # Display Results
                st.markdown("---")
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    st.markdown(f"""
                        <div class="naukri-card score-container">
                            <h3>Match Score</h3>
                            <div class="score-circle">{score}%</div>
                            <p style="margin-top:15px; color:#666;">ATS Compatibility</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("🔍 Missing Keywords & Gaps"):
                        st.write(gaps)
                    
                    if additions:
                        st.warning(f"**To reach 95+ Score:**\n\n{additions}")

                with res_col2:
                    st.markdown('<div class="naukri-card">', unsafe_allow_html=True)
                    st.subheader("✅ Optimized Resume")
                    st.text_area("Copy this content:", rewritten, height=450)
                    
                    st.download_button(
                        label="Download Optimized Resume (.txt)",
                        data=rewritten,
                        file_name="ATS_Optimized_Resume.txt",
                        mime="text/plain"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error parsing results: {e}")
                st.write(raw_result) # Fallback to show raw text if parsing fails
