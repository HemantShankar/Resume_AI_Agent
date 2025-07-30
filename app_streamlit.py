
import streamlit as st
import os
from agent import run_agent

st.set_page_config(page_title="Resume AI Agent", page_icon="🤖")
st.title("🤖 AI Resume Updater")

st.markdown("Upload your **LaTeX Resume** (main.tex) and paste the **Job Description** below")

# === File Upload ===
uploaded_file = st.file_uploader("📄 Upload your LaTeX Resume (main.tex)", type=["tex"])
jd_input = st.text_area("📌 Paste the Job Description")

if st.button("🚀 Generate Updated Resume"):
    if not uploaded_file or not jd_input.strip():
        st.warning("Please upload a LaTeX file and paste a job description.")
    else:
        # Save uploaded file
        tex_path = "main.tex"
        with open(tex_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("⏳ Running AI agent to rewrite resume...")
        output_pdf_path = run_agent(tex_path, jd_input)

        if output_pdf_path and os.path.exists(output_pdf_path):
            with open(output_pdf_path, "rb") as f:
                st.success("✅ Your resume has been updated!")
                st.download_button("⬇️ Download Updated Resume", f, file_name="resume_updated.pdf")
        else:
            st.error("❌ Failed to compile LaTeX to PDF. Please check your file format.")


st.markdown("""
<hr style="border: 0.5px solid #ccc; margin-top: 2em; margin-bottom: 1em"/>

<div style='text-align: center; color: grey; font-size: 1.5em'>
    © 2025 <b>Hemant Shankar</b> | AI agent built using Streamlit and OpenAI
</div>
""", unsafe_allow_html=True)

# Social Media Links (use your own social media URLs)
st.markdown("""
<style>
.social-icons {
    text-align: center;
    padding-top: 20px;
    padding-bottom: 10px;
}
.social-icons a {
    margin: 0 15px;
    display: inline-block;
}
.social-icons img {
    width: 55px;
    height: 55px;
    filter: grayscale(30%);
    transition: filter 0.3s ease, transform 0.3s ease;
}
.social-icons img:hover {
    filter: none;
    transform: scale(1.2);
}
</style>

<div class="social-icons">
    <a href="https://www.linkedin.com/in/hemant-shankar/" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Linkedin_icon.svg" alt="LinkedIn">
    </a>
    <a href="https://www.instagram.com/_hemantshankar_/" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram">
    </a>
    <a href="https://github.com/HemantShankar" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/c2/GitHub_Invertocat_Logo.svg" alt="GitHub">
    </a>
</div>
""", unsafe_allow_html=True)

