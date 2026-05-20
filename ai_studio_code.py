import streamlit as st
import openai
import pypdf
import io

# Page Config
st.set_page_config(page_title="95+ ATS Optimizer", page_icon="📄", layout="centered")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 8px; height: 3em; font-weight: bold; }
    .score-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 95/100 ATS Resume Optimizer")
st.write("Upload your resume and the job description. We will rewrite it to ensure it passes the ATS filters with a top-tier score.")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.info("Get your key at platform.openai.com")

# Inputs
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
with col2:
    jd_text = st.text_area("Paste Job Description", height=200)

if st.button("Analyze & Rewrite for 95+ Score"):
    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    elif not uploaded_file or not jd_text:
        st.error("Please upload a resume and paste a job description.")
    else:
        try:
            # 1. Extract Text
            pdf_reader = pypdf.PdfReader(uploaded_file)
            resume_text = "".join([page.extract_text() for page in pdf_reader.pages])
            
            client = openai.OpenAI(api_key=api_key)

            with st.spinner("🔄 Analyzing and Rewriting..."):
                # 2. AI Logic
                prompt = f"""
                You are an expert ATS (Applicant Tracking System) specialist. 
                
                TASK:
                1. Analyze the Resume against the Job Description (JD).
                2. Calculate a match score (0-100).
                3. Rewrite the resume to score AT LEAST 95/100.
                
                RULES FOR REWRITING:
                - Use standard ATS-friendly headings (SUMMARY, EXPERIENCE, SKILLS, EDUCATION).
                - Use a single-column, text-only layout.
                - Naturally integrate all high-frequency keywords from the JD.
                - Use the 'Action Verb + Task + Result' formula for all bullet points.
                - If the current resume lacks info to hit 95%, use the existing info to maximize the score and list 'REQUIRED ADDITIONS' at the bottom.

                RESUME: {resume_text}
                JD: {jd_text}
                
                OUTPUT FORMAT:
                ---SCORE---
                [Score]/100
                ---ANALYSIS---
                [Brief explanation of gaps]
                ---REWRITTEN RESUME---
                [The full rewritten resume text]
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a professional resume writer."},
                              {"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                result = response.choices[0].message.content

                # 3. Display Results
                st.success("Optimization Complete!")
                
                # Split the result for display
                parts = result.split("---")
                for part in parts:
                    if "SCORE" in part:
                        st.markdown(f"<div class='score-card'><h3>Match Score</h3>{part.replace('SCORE', '')}</div>", unsafe_allow_html=True)
                    elif "ANALYSIS" in part:
                        with st.expander("View Gap Analysis"):
                            st.write(part.replace("ANALYSIS", ""))
                    elif "REWRITTEN RESUME" in part:
                        final_resume = part.replace("REWRITTEN RESUME", "").strip()
                        st.subheader("Optimized Resume")
                        st.text_area("Copy/Paste this into a Word Doc:", final_resume, height=400)
                        
                        st.download_button(
                            label="Download as Text File",
                            data=final_resume,
                            file_name="ATS_Optimized_Resume.txt",
                            mime="text/plain"
                        )
        except Exception as e:
            st.error(f"An error occurred: {e}")