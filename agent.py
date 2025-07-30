import os
import subprocess
from openai import OpenAI
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# === CONFIG ===
# Load the API key from an environment variable
api_key = os.environ.get("OPENAI_API_KEY")

# Check if the API key is available
if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)


OUTPUT_PDF = "output/resume_targeted.pdf"
TEMP_PDF = "main.pdf"

def rewrite_section(jd_text, section_name, current_text):
    prompt = (
        f"You are an expert resume assistant.\n\n"
        f"Your task is to slightly enhance the candidate's **{section_name}** section to better match the following job description:\n"
        f"----- JOB DESCRIPTION -----\n"
        f"{jd_text}\n\n"
        f"----- CURRENT LATEX SECTION ({section_name}) -----\n"
        f"{current_text}\n\n"
        "✅ Only add *relevant technical skills or tools* from the job description that are not already mentioned and keep the original formatting as it is. IF, the keywords are mentioned in bullets, which are seperated with comma, then you have to add the missing keyword add the end of that bullet with a comma. No need to make a sentence, just add keywords with a comma\n"
        "✅ Keep the LaTeX structure, including environments like \\begin{itemize} and \\textbf{}.\n"
        "For Professional Summary, keep the word limit within 35-55 words and in a single paragraph, no need to add multiple points. Keep the text similar to the original text, don't make it look unrealistic, adding every skill is not necessary. Don't include the heading in the text.\n"
        "Don't mention experience in Skills section\n"
        "Try to keep the resume in a single page"
        "✅ Do not rewrite or reformat existing content — just insert missing technologies/tools smartly into the correct line or as a new line in the same LaTeX style.\n"
        "⚠️ Return only the valid LaTeX content inside an existing itemize or list environment (e.g., \\begin{itemize}). Do not introduce free text or section headers.\n"
        # "⚠️ Return only the new LaTeX-formatted body content, ready to be inserted.\n"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
    {"role": "system", "content": "You are a LaTeX-aware resume assistant. Always maintain proper LaTeX formatting and environments."},
    {"role": "user", "content": prompt}
]
    )

    return response.choices[0].message.content.strip()


def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def compile_latex(tex_file):
    compile_cmd = ["pdflatex", "-interaction=nonstopmode", tex_file]
    result = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if os.path.exists(TEMP_PDF):
        os.makedirs("output", exist_ok=True)
        os.replace(TEMP_PDF, OUTPUT_PDF)
        return True
    else:
        print("🚨 LaTeX Error:\n", result.stdout)
        return False


def find_and_replace_section(tex, section_title, new_body):
    pattern = re.compile(
        rf"(\\section{{\\textbf{{{re.escape(section_title)}}}}}.*?)(?=\\section{{\\textbf|\\end{{document}})",
        re.DOTALL
    )
    
    def replacer(match):
        return f"\\section{{\\textbf{{{section_title}}}}}\n{new_body}\n"
    
    return pattern.sub(replacer, tex)

def extract_section(tex, section_title):
    pattern = re.compile(
        rf"\\section{{\\textbf{{{re.escape(section_title)}}}}}(.*?)(?=\\section{{\\textbf|\\end{{document}})",
        re.DOTALL
    )
    match = pattern.search(tex)
    return match.group(1).strip() if match else ""


def run_agent(tex_path, jd_text):
    tex = read_file(tex_path)
    existing_summary = extract_section(tex, "Professional Summary")
    updated_summary = rewrite_section(jd_text, "Professional Summary", existing_summary)
    existing_skills = extract_section(tex, "Technical Skills and Interests")
    updated_skills = rewrite_section(jd_text, "Technical Skills and Interests", existing_skills)


    tex = find_and_replace_section(tex, "Professional Summary", updated_summary)
    tex = find_and_replace_section(tex, "Technical Skills and Interests", updated_skills)

    write_file(tex_path, tex)

    if compile_latex(tex_path):
        print("✅ Resume updated and compiled.")
        return OUTPUT_PDF
    else:
        print("❌ LaTeX compilation failed.")
        return None