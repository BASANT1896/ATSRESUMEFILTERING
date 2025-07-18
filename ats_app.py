import streamlit as st
st.set_page_config(page_title="ATS Resume Expert")  # <-- MUST be the first Streamlit command

from dotenv import load_dotenv
load_dotenv()

# other imports below
import os



import io
import base64
from PIL import Image 
import pdf2image
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input_text, pdf_content, job_description):
    # Use the Gemini 1.5 model
    model = genai.GenerativeModel("models/gemini-1.5-flash")
  # Or 'models/gemini-1.5-flash' for faster/cheaper access

    try:
        # Convert base64-encoded image data back to bytes
        img_bytes = base64.b64decode(pdf_content[0]["data"])

        # Create Gemini-compatible image input part
        img_part = {
            "mime_type": "image/jpeg",
            "data": img_bytes
        }

        # Properly structure the prompt parts: text → image → text
        response = model.generate_content([
            {"text": input_text},
            img_part,
            {"text": job_description}
        ])

        return response.text

    except Exception as e:
        return f"❌ Gemini API error: {e}"



def input_pdf_setup(uploaded_file):
    
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App


st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)...",type=["pdf"])


if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")


submit1 = st.button("Tell Me About the Resume")

#submit2 = st.button("How Can I Improvise my Skills")

submit3 = st.button("Percentage match")

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt1,pdf_content,input_text)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt3,pdf_content,input_text)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")
