import os
import subprocess
import re
from openai import OpenAI
from dotenv import load_dotenv

# === Load API key ===
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

OUTPUT_PDF = "output/resume_targeted.pdf"
TEMP_PDF = "main.pdf"

# === Fix AI responses that forget \begin{itemize} ===
def wrap_items_in_itemize(text):
    lines = text.strip().splitlines()
    items = [line for line in lines if line.strip().startswith(r"\item")]
    if items and not text.strip().startswith(r"\begin{itemize}"):
        return "\\begin{itemize}\n" + "\n".join(items) + "\n\\end{itemize}"
    return text

# === Rewrite Resume Section ===
def rewrite_section(jd_text, section_name, current_text):
    prompt = (
        f"You are an expert LaTeX resume assistant.\n\n"
        f"Enhance the **{section_name}** section to better match this job description:\n"
        f"----- JOB DESCRIPTION -----\n{jd_text}\n\n"
        f"----- CURRENT SECTION -----\n{current_text}\n\n"
        "✅ Add only relevant *technical skills/tools* from the JD not already mentioned.\n"
        "✅ If bullet items are comma-separated, append missing keywords at the end.\n"
        "✅ Keep the original LaTeX structure intact, especially environments like \\begin{itemize}.\n"
        "✅ For 'Professional Summary', limit to 35–55 words in a single paragraph (no headings).\n"
        "❌ Do not mention experience inside the Skills section.\n"
        "⚠️ Return ONLY the LaTeX-formatted content. Do not add new sections or text.\n"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a LaTeX-aware resume assistant. Always maintain proper LaTeX formatting."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_response = response.choices[0].message.content.strip()
    return wrap_items_in_itemize(ai_response)

# === Read / Write Files ===
def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# === Compile LaTeX to PDF ===
def compile_latex(tex_file):
    compile_cmd = ["pdflatex", "-interaction=nonstopmode", tex_file]
    result = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Save log output for debugging
    os.makedirs("output", exist_ok=True)
    with open("output/latex_debug.log", "w", encoding="utf-8") as f:
        f.write(result.stdout + "\n" + result.stderr)

    if os.path.exists(TEMP_PDF):
        os.replace(TEMP_PDF, OUTPUT_PDF)
        return True
    else:
        print("❌ LaTeX compilation failed. See output/latex_debug.log for details.")
        return False

# === Find & Replace Section Content ===
def find_and_replace_section(tex, section_title, new_body):
    pattern = re.compile(
        rf"(\\section{{\\textbf{{{re.escape(section_title)}}}}}.*?)(?=\\section{{\\textbf|\\end{{document}})",
        re.DOTALL
    )
    def replacer(_):
        return f"\\section{{\\textbf{{{section_title}}}}}\n{new_body}\n"
    return pattern.sub(replacer, tex)

# === Extract Old Section ===
def extract_section(tex, section_title):
    pattern = re.compile(
        rf"\\section{{\\textbf{{{re.escape(section_title)}}}}}(.*?)(?=\\section{{\\textbf|\\end{{document}})",
        re.DOTALL
    )
    match = pattern.search(tex)
    return match.group(1).strip() if match else ""

# === Orchestrate the Resume Rewrite ===
def run_agent(tex_path, jd_text):
    tex = read_file(tex_path)

    # Extract existing sections
    summary = extract_section(tex, "Professional Summary")
    skills = extract_section(tex, "Technical Skills and Interests")

    # Generate updates via OpenAI
    updated_summary = rewrite_section(jd_text, "Professional Summary", summary)
    updated_skills = rewrite_section(jd_text, "Technical Skills and Interests", skills)

    # Replace old sections with new ones
    tex = find_and_replace_section(tex, "Professional Summary", updated_summary)
    tex = find_and_replace_section(tex, "Technical Skills and Interests", updated_skills)

    # Save & compile
    write_file(tex_path, tex)
    if compile_latex(tex_path):
        print("✅ Resume updated and compiled successfully.")
        return OUTPUT_PDF
    else:
        return None
