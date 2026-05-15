# Recruiter Notes Generator

A Streamlit-based tool for recruiters to summarize screening conversations into non-biased bullet points for hiring managers.

## Features
- Input fields and file upload support (.txt, .pdf, .docx) for Job Description and Candidate Conversation/Notes.
- Integration with Gemini AI (via `google-generativeai`) to generate summaries.
- Non-biased, objective bullet points highlighting key discussion points.
- Downloadable Markdown summary.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Gemini API Key:**
   - Obtain a Gemini API Key from the [Google AI Studio](https://aistudio.google.com/).
   - You can either:
     - Enter the key directly in the app's sidebar.
     - Set an environment variable: `export GOOGLE_API_KEY='your_api_key_here'`
     - Create a `.env` file in the project root with: `GOOGLE_API_KEY=your_api_key_here`

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Usage
1. Paste the **Job Description** in the left text area.
2. Paste the **Candidate Conversation/Notes** in the right text area.
3. Click **Generate Notes**.
4. Review the generated summary and download it if needed.
