import os
import streamlit as st
import google.generativeai as genai
from file_handler.docx_handler import extract_docx_content
from file_handler.ppt_handler import extract_pptx_content
from file_handler.pdf_handler import extract_pdf_content

genai.configure(api_key="GEMINI_API_KEY")

def extract_content(file_path):
    try:
        if os.path.basename(file_path).startswith("~$"):
            return {"text":[], "images":[], "tables":[]}
        file_type=file_path.split(".")[-1].lower()
        if file_type=="pdf":
            return extract_pdf_content(file_path)
        elif file_type=="docx":
            return extract_docx_content(file_path)
        elif file_type=="pptx":
            return extract_pptx_content(file_path)
        else:
            return {"text":[], "images":[], "tables":[]} 
    except Exception as e:
        st.error(f"Error processing file {file_path}: {e}")
        return {"text":[], "images":[], "tables":[]} 

def extract_from_folder(folder_path):
    all_text=""
    for file_name in os.listdir(folder_path):
        file_path=os.path.join(folder_path,file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith((".pdf",".docx",".pptx")):
            text=extract_content(file_path)["text"]
            for page_text in text:
                if page_text.strip():
                    all_text+=f"\n\n=== {file_name} ===\n{page_text}"
    return all_text.strip()

def query_gemini_api(document_text, user_query):
    prompt=f"Based on the following documents:\n\n{document_text}\n\nAnswer this query: {user_query}"
    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt)
    return response.text if response else "No response from Gemini."

# Streamlit UI
st.title("Crambot: Powered by YOUR notes!")
folder=st.file_uploader("Upload a folder containing documents:", accept_multiple_files=True)
if folder:
    folder_path="uploaded_files"
    os.makedirs(folder_path, exist_ok=True)
    for file in folder:
        file_path=os.path.join(folder_path, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    st.success("Folder uploaded successfully! Processing files...")
    document_text=extract_from_folder(folder_path)
    if not document_text:
        st.error("Error: No text extracted from the documents.")
    else:
        st.session_state["document_text"]=document_text
        st.success("Documents processed successfully! You can now ask questions.")

if "document_text" in st.session_state:
    user_query=st.text_input("Ask a question:")
    if st.button("Send") and user_query:
        response=query_gemini_api(st.session_state["document_text"], user_query)
        st.write("Chatbot:", response)
