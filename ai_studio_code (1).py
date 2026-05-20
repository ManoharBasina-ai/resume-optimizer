import streamlit as st
import openai
import pypdf
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Resume Score & Optimizer | Naukri Style", page_icon="💼", layout="wide")

# --- NAUKRI THEME CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f4f7fa;
    }

    /* Header Simulation */
    .nav-bar {
        background-color: #ffffff;
        padding: 15px 100px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e6e6e6;
        margin-bottom: 30px;
    }
    
    .naukri-logo {
        color: #457eff;
        font-size: 28px;
        font-weight: 800;
        font-family: 'Roboto', sans-serif;
    }

    /* Card Styling */
    .naukri-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #457eff;
        color: white;
        border-radius: 50px;
        padding: 10px 25px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #270b5d;
        color: white;
    }

    /* Score Circle */
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: #f0faff;
        border: 5px solid #457eff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: bold;
        color: #457eff;
        margin: 0 auto;
    }

    /* Text Inputs */
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #d3d3d3;
    }
    </style>
    
    <div class="nav-bar">
        <div class="naukri-logo">naukri <span style="color:#333">clone</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    pdf_reader = pypdf.PdfReader(uploaded_file)
    return "".join([page.extract_text() for page in pdf_reader.pages])

def call_ai(prompt, api_key):
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a Senior Recruitment Consultant at a top firm."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

# --- UI LAYOUT ---
st.markdown("<h1 style='text-align: center; color: #270b5d;'>Get your resume noticed by top recruiters</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Analyze, Rate, and Rewrite your resume to a 95+ ATS Score</p>", unsafe_allow_html=True)

# Sidebar for API Key
with st.sidebar:
    st.image("https://static.naukimg.com/s/4/100/i/naukri_Logo.png", width=150)
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("---")
    st.write("This tool uses AI to match your profile with Job Descriptions.")

# Main Content Area
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="naukri-card">', unsafe_allow_html=True)
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Choose PDF file", type="pdf", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="naukri-card">', unsafe_allow_html=True)
    st.subheader("2. Job Description")
    jd_text = st.text_area("Paste the target job description here", height=150, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("Check Score & Rewrite"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
    elif uploaded_file and jd_text:
        resume_text = extract_text_from_pdf(uploaded_file)
        
        # Step 1: Analysis
        with st.spinner("Calculating ATS Match..."):
            analysis_prompt = f"""
            Compare this Resume and JD. 
            1. Provide a Match Score (0-100).
            2. List missing skills.
            3. State if 95/100 is possible with current info.
            Resume: {resume_text}
            JD: {jd_text}
            Format: Score: [X] | Missing: [list] | Possible: [Yes/No]
            """
            analysis_result = call_ai(analysis_prompt, api_key)
            
            # Display Score in Naukri Style
            score = analysis_result.split("|")[0].split(":")[1].strip()
            st.markdown(f"""
                <div class="naukri-card" style="text-align:center;">
                    <h3>Your ATS Match Score</h3>
                    <div class="score-circle">{score}%</div>
                </div>
            """, unsafe_allow_html=True)

        # Step 2: Rewriting
        with st.spinner("Rewriting for 95+ Score..."):
            rewrite_prompt = f"""
            Rewrite the resume to achieve a 95/100 ATS score for this JD.
            - Use professional, clean formatting.
            - Use Action Verbs (e.g., 'Spearheaded', 'Optimized').
            - Include all missing keywords from the JD.
            - If info is missing, use [PLACEHOLDER] but ensure the structure is perfect.
            Resume: {resume_text}
            JD: {jd_text}
            """
            rewritten_text = call_ai(rewrite_prompt, api_key)
            
            st.markdown('<div class="naukri-card">', unsafe_allow_html=True)
            st.subheader("✅ Optimized Resume (ATS Friendly)")
            st.text_area("Copy the content below:", rewritten_text, height=400)
            
            st.download_button(
                label="Download Optimized Resume",
                data=rewritten_text,
                file_name="Naukri_Optimized_Resume.txt",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Please provide both a resume and a job description.")