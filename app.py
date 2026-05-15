import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
import docx
import io

# Load environment variables from .env file if it exists
load_dotenv()

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension == ".txt":
        return uploaded_file.getvalue().decode("utf-8")
    elif file_extension == ".pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_extension == ".docx":
        doc = docx.Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        return ""

def generate_notes(job_description, candidate_conversation, api_key):
    if not api_key:
        st.error("Please provide a Gemini API Key.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""
        You are an expert recruiter assistant. Your task is to summarize a candidate screening conversation based on a Job Description.
        
        Job Description:
        {job_description}
        
        Candidate Conversation/Notes:
        {candidate_conversation}
        
        Please provide a summary of the conversation in clear, non-biased bullet points. 
        Focus on:
        - Key points discussed during the conversation.
        - How the candidate's experience and skills align with the job requirements.
        - Any specific details mentioned by the candidate (availability, salary expectations, etc.).
        
        Maintain a professional and objective tone. Do not include personal opinions or biases.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def main():
    st.set_page_config(page_title="Recruiter Notes Generator", page_icon="📝", layout="wide")
    
    st.title("📝 Recruiter Notes Generator")
    st.markdown("""
    This tool helps recruiters summarize screening conversations into non-biased bullet points for hiring managers.
    You can either paste text directly or upload files (.txt, .pdf, .docx).
    """)

    # Sidebar for API Key
    with st.sidebar:
        st.title("Configuration")
        api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
        if not api_key:
            st.warning("Please enter your Gemini API Key to proceed.")
        st.markdown("---")
        st.markdown("Developed for the Recruiter Notes Team")

    # Initialize session state for text areas if not present
    if 'job_desc_text' not in st.session_state:
        st.session_state['job_desc_text'] = ""
    if 'candidate_notes_text' not in st.session_state:
        st.session_state['candidate_notes_text'] = ""

    # Main input areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Job Description")
        uploaded_jd = st.file_uploader("Upload Job Description", type=["txt", "pdf", "docx"], key="jd_uploader")
        if uploaded_jd:
            st.session_state['job_desc_text'] = extract_text_from_file(uploaded_jd)
        
        job_description = st.text_area(
            "Paste or edit Job Description", 
            value=st.session_state['job_desc_text'],
            height=300, 
            placeholder="Paste the job description here..."
        )
        
    with col2:
        st.subheader("Candidate Conversation/Notes")
        uploaded_notes = st.file_uploader("Upload Candidate Notes", type=["txt", "pdf", "docx"], key="notes_uploader")
        if uploaded_notes:
            st.session_state['candidate_notes_text'] = extract_text_from_file(uploaded_notes)
            
        candidate_conversation = st.text_area(
            "Paste or edit Candidate Conversation/Notes", 
            value=st.session_state['candidate_notes_text'],
            height=300, 
            placeholder="Paste the screening notes or conversation transcript here..."
        )

    if st.button("Generate Notes"):
        if job_description and candidate_conversation:
            with st.spinner("Generating summary..."):
                notes = generate_notes(job_description, candidate_conversation, api_key)
                if notes:
                    st.divider()
                    st.subheader("Generated Recruiter Notes")
                    st.markdown(notes)
                    st.download_button(
                        label="Download Notes",
                        data=notes,
                        file_name="recruiter_notes.md",
                        mime="text/markdown"
                    )
        else:
            if not job_description:
                st.error("Please provide a Job Description.")
            if not candidate_conversation:
                st.error("Please provide Candidate Conversation/Notes.")

if __name__ == "__main__":
    main()
