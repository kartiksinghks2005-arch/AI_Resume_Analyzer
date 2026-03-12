import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from groq import Groq
import os
import json
import re
from sentence_transformers import SentenceTransformer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import tempfile
from sklearn.metrics.pairwise import cosine_similarity

# -------- LOAD SEMANTIC MODEL --------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ---------------- LOAD SKILLS DATABASE ----------------
with open("skills_database.json", "r") as file:
    skills_data = json.load(file)

skills_list = []

for category in skills_data.values():
    skills_list.extend(category)

skills_list = list(set(skills_list))

# ---------------- LOAD JOB ROLES ----------------
with open("job_roles.json", "r") as file:
    job_roles = json.load(file)

# ---------------- GROQ CLIENT ----------------
client = Groq(api_key="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")

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# -------- MODERN DASHBOARD STYLE --------
st.markdown("""
<style>



.block-container{
padding-top:2rem;
padding-bottom:2rem;
padding-left:4rem;
padding-right:4rem;
}

[data-testid="metric-container"]{
background-color:#1e222b;
border-radius:10px;
padding:15px;
box-shadow:0px 0px 10px rgba(0,0,0,0.3);
}

.stProgress > div > div{
background:linear-gradient(90deg,#00DBDE,#FC00FF);
}

</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Resume Analyzer PRO")

st.markdown(
"""
AI-powered **resume screening platform** that analyzes resumes,
detects skills, predicts job roles, and ranks candidates automatically.
"""
)

# ---------------- ADVANCED ATS SCORE FUNCTION ----------------
def calculate_advanced_ats_score(text, detected_skills, job_description=None):

    score = 0
    text = text.lower()

    if "@" in text:
        score += 10

    if re.search(r'\+?\d[\d\s-]{8,}', text):
        score += 5

    if "linkedin" in text or "github" in text:
        score += 5

    sections = ["skills", "projects", "experience", "education", "certification"]

    for sec in sections:
        if sec in text:
            score += 5

    skill_count = len(detected_skills)

    if skill_count >= 15:
        score += 25
    elif skill_count >= 10:
        score += 20
    elif skill_count >= 5:
        score += 15
    elif skill_count >= 3:
        score += 10
    else:
        score += 5

    if "internship" in text:
        score += 5

    if "project" in text:
        score += 5

    if "developed" in text or "built" in text or "implemented" in text:
        score += 5

    if job_description:
        jd_words = re.findall(r'\b\w+\b', job_description.lower())
        match_count = 0

        for word in jd_words:
            if word in text:
                match_count += 1

        keyword_score = min(match_count / 20 * 15, 15)

        score += keyword_score

    return int(min(score, 100))

def semantic_match_score(resume_text, job_description):

    if not job_description:
        return 0

    resume_embedding = model.encode([resume_text])
    jd_embedding = model.encode([job_description])

    similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]

    return int(similarity * 100)
# ---------------- SECTION DETECTION ----------------
def detect_sections(text):

    sections = ["education","experience","skills","projects","certification"]

    results = {}

    for sec in sections:
        if sec in text:
            results[sec] = True
        else:
            results[sec] = False

    return results


# ---------------- PDF REPORT GENERATION ----------------
def generate_pdf(name, resume_score, match_percent, skills):

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    c = canvas.Canvas(temp_file.name, pagesize=letter)

    c.setFont("Helvetica",12)

    y = 750

    c.drawString(100,y,"AI Resume Analyzer Report")
    y -= 40

    c.drawString(100,y,f"Candidate: {name}")
    y -= 30

    c.drawString(100,y,f"Resume Score: {resume_score}")
    y -= 30

    c.drawString(100,y,f"Job Match Score: {match_percent}%")
    y -= 30

    c.drawString(100,y,"Detected Skills:")
    y -= 20

    for skill in skills[:20]:
        c.drawString(120,y,skill)
        y -= 15

    c.save()

    return temp_file.name

# ---------------- MULTIPLE FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Resume(s) (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# ---------------- JOB DESCRIPTION INPUT ----------------
st.subheader("📄 Job Description (Optional for Candidate Ranking)")

job_description = st.text_area(
    "Paste Job Description to Rank Multiple Resumes"
)



ranking_results = []
table_data = []

# ---------------- PROCESS RESUMES ----------------
if uploaded_files:

    for uploaded_file in uploaded_files:

        file_type = uploaded_file.name.split(".")[-1]

        if file_type == "pdf":
            resume_text = extract_text_from_pdf(uploaded_file)

        elif file_type == "docx":
            resume_text = extract_text_from_docx(uploaded_file)

        elif file_type == "txt":
            resume_text = extract_text_from_txt(uploaded_file)

        resume_text = resume_text.lower()

        # -------- SKILL DETECTION --------
        detected_skills = []

        for skill in skills_list:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, resume_text):
                detected_skills.append(skill)

        detected_skills = sorted(list(set(detected_skills)))

        
        # -------- ATS SCORE --------
        ats_score = calculate_advanced_ats_score(
        resume_text,
        detected_skills,
        job_description
        )
        # -------- AI SEMANTIC MATCH --------
        semantic_score = semantic_match_score(resume_text, job_description)

        # -------- JOB DESCRIPTION MATCH --------
        score = 0

        if job_description:

            for skill in skills_list:
                if skill in resume_text and skill in job_description.lower():
                    score += 1

            ranking_results.append({
                "Candidate": uploaded_file.name,
                "Score": score,
                "Skills": len(detected_skills)
            })

        # -------- RESUME SCORE --------
        resume_score = 0

        resume_score += len(detected_skills) * 5

        if "projects" in resume_text:
            resume_score += 20

        if "experience" in resume_text:
            resume_score += 20

        if "education" in resume_text:
            resume_score += 10

        resume_score = min(resume_score, 100)

        table_data.append({
                  
           "Candidate": uploaded_file.name.replace(".txt",""),
           "Skills Found": len(detected_skills),
           "ATS Score": ats_score,
           "Resume Score": resume_score,
           "AI Match": semantic_score if job_description else 0
            })

        # -------- FULL ANALYSIS FOR FIRST RESUME --------
        if uploaded_file == uploaded_files[0]:

            st.subheader("📃 Extracted Resume Text")
            st.text_area("Resume Content", resume_text[:1000])

            # -------- SECTION DETECTION --------
            st.subheader("📑 Resume Section Analysis")

            sections = detect_sections(resume_text)

            for sec, found in sections.items():

                if found:
                    st.success(f"{sec.title()} Section Found")

                else:
                    st.warning(f"{sec.title()} Section Missing")

            # -------- SKILLS --------
            st.subheader("💡 Detected Skills")

            if detected_skills:
                st.success(", ".join(detected_skills))
            else:
                st.warning("No skills detected")

            # -------- ATS SCORE --------
            st.subheader("🤖 ATS Compatibility")

            st.progress(ats_score)
            st.write(f"ATS Score: {ats_score}%")

            # -------- ROLE PREDICTION --------
            st.subheader("🧠 Suggested Job Roles")

            role_scores = {}

            for role, role_skills in job_roles.items():

                matched = 0

                for skill in role_skills:
                    if skill in detected_skills:
                        matched += 1

                role_scores[role] = matched / len(role_skills)

            sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
            top_roles = sorted_roles[:5]

            cols = st.columns(3)

            for i, (role, score) in enumerate(top_roles):

                percentage = int(score * 100)

                if percentage > 0:

                    with cols[i % 3]:

                        st.metric(
                            label=f"#{i+1} {role}",
                            value=f"{percentage}% match"
                        )

                        st.progress(percentage / 100)

            # -------- TARGET ROLE --------
            st.subheader("🎯 Target Job Role")

            selected_role = st.selectbox(
                "Choose Job Role",
                list(job_roles.keys())
            )

            required_skills = job_roles[selected_role]

            missing_skills = []

            for skill in required_skills:
                if skill not in detected_skills:
                    missing_skills.append(skill)

            match_percent = int(((len(required_skills) - len(missing_skills)) / len(required_skills)) * 100)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("📊 Resume Strength Score")
                st.progress(resume_score)
                st.write(f"Score: {resume_score}/100")

            with col2:
                st.subheader("📈 Job Match Score")
                st.progress(match_percent)
                st.write(f"Match Percentage: {match_percent}%")
            
            with col3:
                st.subheader("🧠 AI Semantic Match")
                st.progress(semantic_score)
                st.write(f"AI Match Score: {semantic_score}%")

            # -------- WORD CLOUD --------
            st.subheader("☁ Resume Word Cloud")

            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color="white"
            ).generate(resume_text)

            fig, ax = plt.subplots()
            ax.imshow(wordcloud)
            ax.axis("off")

            st.pyplot(fig)

            # -------- PDF REPORT --------
            st.subheader("📄 Download Resume Report")

            pdf_path = generate_pdf(
                uploaded_file.name,
                resume_score,
                match_percent,
                detected_skills
            )

            with open(pdf_path,"rb") as f:

                st.download_button(
                    "Download Resume Report",
                    f,
                    file_name="resume_report.pdf"
                )

            # -------- AI FEEDBACK --------
            st.subheader("🤖 AI Resume Feedback")

            if st.button("Generate AI Feedback"):

                prompt = f"""
                Analyze the following resume and give professional feedback.

                Resume:
                {resume_text}

                Provide:
                1. Strengths
                2. Weaknesses
                3. Suggestions for improvement
                """

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )

                feedback = response.choices[0].message.content

                st.write(feedback)

# ---------------- CANDIDATE RANKING ----------------
if ranking_results:

    st.subheader("🏆 Candidate Ranking Dashboard")

    jd_skills = []

    for skill in skills_list:
        if job_description and skill in job_description.lower():
            jd_skills.append(skill)

    total_jd_skills = len(jd_skills)

    table = []

    for candidate in ranking_results:

        name = candidate["Candidate"]
        score = candidate["Score"]
        skills_found = candidate["Skills"]

        if total_jd_skills > 0:
            percentage = int((score / total_jd_skills) * 100)
        else:
            percentage = 0

        if percentage > 80:
            fit = "Excellent"
            medal = "🥇"
        elif percentage > 50:
            fit = "Good"
            medal = "🥈"
        else:
            fit = "Low"
            medal = "🥉"

        table.append({
            "Rank": medal,
            "Candidate": name,
            "Match %": percentage,
            "Skills Found": skills_found,
            "Fit": fit
        })

    df = pd.DataFrame(table)

    st.dataframe(df, use_container_width=True)
# ---------------- CANDIDATE TABLE ----------------
if table_data:

    st.subheader("📊 Candidate Comparison Table")

    df = pd.DataFrame(table_data)

    df = df.sort_values(by="Resume Score", ascending=False)

    df.index = df.index + 1

    st.dataframe(df, use_container_width=True)

