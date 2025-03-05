import streamlit as st
import os
os.environ["OPENAI_API_KEY"] = "sk-YOUR API KEY"
import io
from src.generator import Generator
from src.utils import load_openai_key
import base64
from dotenv import load_dotenv
from PIL import Image
import pdf2image
import google.generativeai as genai
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=API_KEY)

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        pdf_parts = [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr).decode()}]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Set page config
st.set_page_config(page_title="Resume Expert", page_icon="📝", layout="wide")

# Header
st.title("\U0001F4C4 AI-Powered Resume Screening System")
st.subheader("\U0001F680 Evaluate your Resume Against a Job Description")


# Layout
col1, col2 = st.columns([2, 1])
with col1:
    input_text = st.text_area("**\U0001F50D Job Description:**", key="input")
with col2:
    uploaded_file = st.file_uploader("\U0001F4C2 Upload your Resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        st.success("✅ Resume Uploaded Successfully!")

# Buttons
col3, col4, col5 = st.columns([1, 1, 1])
with col3:
    submit1 = st.button("\U0001F4CA Evaluate Resume")

with col4:
    submit3 = st.button("\U0001F4CA Percentage Match with Job Description")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Review the provided resume against the job description. 
Provide an evaluation highlighting strengths and weaknesses.
"""
input_prompt3 = """
You are an ATS scanner. Evaluate the resume against the job description. 
Give a percentage match, missing keywords, and final thoughts.
"""

# Handling button clicks
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("📊 Evaluation Result")
        st.write(response)
    else:
        st.warning("⚠️ Please upload your resume first!")

if submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("📊 Percentage Match Result")
        st.write(response)
    else:
        st.warning("⚠️ Please upload your resume first!")

# Load descriptions if not in session state
if 'cv_desc' not in st.session_state:
    with open("data/cv.md", "r") as file:
        st.session_state.cv_desc = file.read()
if 'job_desc' not in st.session_state:
    with open("data/job.md", "r") as job_file:
        st.session_state.job_desc = job_file.read()

height = 800
col_cv, col_job, col_questions = st.columns([1, 1, 1.5])
with col_cv:
    st.subheader("CV", divider="blue")
    with st.container():
        @st.fragment
        def update_cv_text_area():
            """Update the text area of the CV"""
            st.session_state.cv_desc = st.text_area("Enter your CV here", value=st.session_state.cv_desc, height=height)
        update_cv_text_area()
with col_job:
    st.subheader("Job Description", divider="blue")
    with st.container():
        @st.fragment
        def update_job_description():
            """Update the text area of the job description"""
            st.text_area("Enter your job description here", value=st.session_state.job_desc, height=height, key="job_desc_input")
        update_job_description()
with col_questions:
    st.subheader("Generated Questions", divider="green")
    with st.container(border=True, height=height+32):
        @st.fragment
        def generate_questions_fragment():
            """Generate questions"""
            if st.button("Generate Questions", key="generate_questions"):
                if API_KEY:
                    data = {"cv": st.session_state.cv_desc, "job": st.session_state.job_desc}
                    if len(st.session_state.cv_desc) == 0:
                        st.error("Please enter your CV")
                    elif len(st.session_state.job_desc) == 0:
                        st.error("Please enter the job description")
                    else:
                        gen = Generator(data=data, key=API_KEY)
                        questions = gen.generate()
                        st.write(questions)
                else:
                    st.error("Please enter your OpenAI key")
        generate_questions_fragment()
