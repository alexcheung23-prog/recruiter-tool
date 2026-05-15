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

def get_gemini_model(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-flash-latest')

def generate_notes(job_description, candidate_conversation, api_key):
    if not api_key:
        st.error("Please provide a Gemini API Key.")
        return None

    try:
        model = get_gemini_model(api_key)
        
        prompt = f"""
        You are an expert recruiter assistant. Your task is to provide a detailed, structured, and professional summary of a candidate screening conversation based on the provided Job Description.

        ### Job Description:
        {job_description}

        ### Candidate Conversation/Notes:
        {candidate_conversation}

        ### Output Requirements:
        Please provide a comprehensive summary formatted for a hiring manager. Structure the notes into the following sections:

        1. **Executive Summary**: A high-level overview of the candidate and the overall impression of the conversation.
        2. **Detailed Topic/Question Breakdown**:
           - Break this section down by the specific topics or questions discussed during the interview.
           - **Include specific examples, stories, or achievements** mentioned by the candidate for each topic.
        3. **Job Description Alignment**:
           - Explicitly map the candidate's skills and experience to the requirements listed in the Job Description.
           - Highlight where they are a strong match and note any gaps.
        4. **Logistics & Next Steps**:
           - Mention specific details like salary expectations, notice period, availability for next rounds, and any other administrative details discussed.

        ### Guidelines:
        - **Objective & Non-Biased**: Stick to the facts of the conversation. Avoid subjective language.
        - **Presentable**: Use clear headings, bold text for emphasis, and bullet points for readability.
        - **Detailed**: Ensure specific examples from the candidate are captured to provide context to the hiring manager.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred during generation: {e}")
        return None

def refine_notes(job_description, candidate_conversation, previous_notes, refinement_instructions, api_key):
    if not api_key:
        st.error("Please provide a Gemini API Key.")
        return None

    try:
        model = get_gemini_model(api_key)
        
        prompt = f"""
        You are an expert recruiter assistant. You have previously generated a summary of a candidate screening conversation. The user now wants to refine or reformat that summary.

        ### Job Description:
        {job_description}

        ### Candidate Conversation/Notes:
        {candidate_conversation}

        ### Previous Summary:
        {previous_notes}

        ### Refinement Instructions from the Recruiter:
        "{refinement_instructions}"

        ### Task:
        Please update the summary based on the instructions above. 
        - If the user asks to "reformat", "shorten", or "focus on X", prioritize those instructions.
        - Ensure the output remains professional, objective, and structured.
        - If not specified otherwise, maintain the detailed sections (Executive Summary, Detailed Breakdown, Alignment, Logistics).
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred during refinement: {e}")
        return None

def main():
    st.set_page_config(page_title="Recruiter Notes Generator", page_icon="📝", layout="wide")
    
    st.title("📝 Recruiter Notes Generator")
    st.markdown("""
    This tool helps recruiters summarize screening conversations into detailed, non-biased bullet points for hiring managers.
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

    # Initialize session state
    if 'generated_notes' not in st.session_state:
        st.session_state['generated_notes'] = ""
    if 'job_desc_text' not in st.session_state:
        st.session_state['job_desc_text'] = ""
    if 'candidate_notes_text' not in st.session_state:
        st.session_state['candidate_notes_text'] = ""

    # Main input areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Job Description")
        def handle_jd_upload():
            if st.session_state.jd_uploader:
                text = extract_text_from_file(st.session_state.jd_uploader)
                if text:
                    st.session_state.jd_area = text
                else:
                    st.error("Could not extract text from the uploaded Job Description.")

        st.file_uploader(
            "Upload Job Description", 
            type=["txt", "pdf", "docx"], 
            key="jd_uploader", 
            on_change=handle_jd_upload
        )
        
        job_description = st.text_area(
            "Paste or edit Job Description", 
            height=300, 
            placeholder="Paste the job description here...",
            key="jd_area"
        )
        
    with col2:
        st.subheader("Candidate Conversation/Notes")
        def handle_notes_upload():
            if st.session_state.notes_uploader:
                text = extract_text_from_file(st.session_state.notes_uploader)
                if text:
                    st.session_state.notes_area = text
                else:
                    st.error("Could not extract text from the uploaded Candidate Notes.")

        st.file_uploader(
            "Upload Candidate Notes", 
            type=["txt", "pdf", "docx"], 
            key="notes_uploader",
            on_change=handle_notes_upload
        )
            
        candidate_conversation = st.text_area(
            "Paste or edit Candidate Conversation/Notes", 
            height=300, 
            placeholder="Paste the screening notes or conversation transcript here...",
            key="notes_area"
        )

    if st.button("Generate Notes"):
        if job_description and candidate_conversation:
            with st.spinner("Generating summary..."):
                notes = generate_notes(job_description, candidate_conversation, api_key)
                if notes:
                    st.session_state['generated_notes'] = notes
        else:
            if not job_description:
                st.error("Please provide a Job Description.")
            if not candidate_conversation:
                st.error("Please provide Candidate Conversation/Notes.")

    # Display and Refine Notes
    if st.session_state['generated_notes']:
        st.divider()
        st.subheader("Recruiter Notes")
        st.markdown(st.session_state['generated_notes'])
        
        st.download_button(
            label="Download Notes",
            data=st.session_state['generated_notes'],
            file_name="recruiter_notes.md",
            mime="text/markdown"
        )

        st.subheader("Refine Notes")
        st.info("You can 'talk back' to the tool to reformat, shorten, or change the focus of the notes above. For example, you can say 'make it more concise' or 'elaborate more on the technical skills section'.")
        refinement_instructions = st.text_input("Refinement Instructions", key="refinement_input", placeholder="Enter instructions to adjust the notes...")
        if st.button("Apply Refinement"):
            if refinement_instructions:
                with st.spinner("Refining summary..."):
                    refined_notes = refine_notes(
                        job_description, 
                        candidate_conversation, 
                        st.session_state['generated_notes'], 
                        refinement_instructions, 
                        api_key
                    )
                    if refined_notes:
                        st.session_state['generated_notes'] = refined_notes
                        st.rerun()
            else:
                st.warning("Please enter refinement instructions.")

if __name__ == "__main__":
    main()
