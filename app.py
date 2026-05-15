import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def generate_notes(job_description, candidate_conversation, api_key):
    if not api_key:
        st.error("Please provide a Gemini API Key.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
    st.set_page_config(page_title="Recruiter Notes Generator", page_icon="📝")
    
    st.title("📝 Recruiter Notes Generator")
    st.markdown("""
    This tool helps recruiters summarize screening conversations into non-biased bullet points for hiring managers.
    """)

    # Sidebar for API Key
    with st.sidebar:
        st.title("Configuration")
        api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
        if not api_key:
            st.warning("Please enter your Gemini API Key to proceed.")
        st.markdown("---")
        st.markdown("Developed for the Recruiter Notes Team")

    # Main input areas
    col1, col2 = st.columns(2)
    
    with col1:
        job_description = st.text_area("Job Description", height=300, placeholder="Paste the job description here...")
        
    with col2:
        candidate_conversation = st.text_area("Candidate Conversation/Notes", height=300, placeholder="Paste the screening notes or conversation transcript here...")

    if st.button("Generate Notes"):
        if job_description and candidate_conversation:
            with st.spinner("Generating summary..."):
                notes = generate_notes(job_description, candidate_conversation, api_key)
                if notes:
                    st.subheader("Generated Recruiter Notes")
                    st.markdown(notes)
                    st.download_button(
                        label="Download Notes",
                        data=notes,
                        file_name="recruiter_notes.md",
                        mime="text/markdown"
                    )
        else:
            st.error("Please provide both the Job Description and the Candidate Conversation.")

if __name__ == "__main__":
    main()
