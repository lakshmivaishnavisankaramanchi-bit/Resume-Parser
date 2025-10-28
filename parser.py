import re
import os
import PyPDF2
import docx
import spacy
import pandas as pd

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to extract basic details using regex + NLP
def extract_details(text):
    details = {}

    # Extract email
    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    details["Email"] = email[0] if email else "Not Found"

    # Extract phone number
    phone = re.findall(r"\+?\d[\d -]{8,12}\d", text)
    details["Phone"] = phone[0] if phone else "Not Found"

    # Extract name (simple assumption – first PERSON entity)
    doc = nlp(text)
    name = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    details["Name"] = name[0] if name else "Not Found"

    return details

# Function to extract skills
def extract_skills(text):
    with open("skills.txt", "r") as f:
        skill_list = [line.strip().lower() for line in f.readlines()]
    found_skills = [skill for skill in skill_list if skill in text.lower()]
    return ", ".join(found_skills) if found_skills else "Not Found"

# Process all resumes
data = []
folder = "resumes"

for file in os.listdir(folder):
    path = os.path.join(folder, file)
    print(f"Processing: {file}")

    if file.endswith(".pdf"):
        text = extract_text_from_pdf(path)
    elif file.endswith(".docx"):
        text = extract_text_from_docx(path)
    else:
        continue

    details = extract_details(text)
    details["Skills"] = extract_skills(text)
    details["File Name"] = file

    data.append(details)

# Save extracted data
df = pd.DataFrame(data)
df.to_csv("output.csv", index=False)
print("\n✅ Extraction complete! Results saved to 'output.csv'")
