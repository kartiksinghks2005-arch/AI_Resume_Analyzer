import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from groq import Groq
import os
import json
import re
from sentence_transformers import SentenceTransformer

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

[data-testid="stAppViewContainer"]{
background-color:#0e1117;
color:white;
}

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

# ---------------- JOB DESCRIPTION INPUT ----------------
st.subheader("📄 Job Description (Optional for Candidate Ranking)")

job_description = st.text_area(
    "Paste Job Description to Rank Multiple Resumes"
)

# ---------------- MULTIPLE FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Resume(s) (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

ranking_results = []

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

        # -------- JOB DESCRIPTION MATCH (RANKING) --------
        if job_description:

            score = 0

            for skill in skills_list:
                if skill in resume_text and skill in job_description.lower():
                    score += 1

            ranking_results.append((uploaded_file.name, score))

        # -------- FULL ANALYSIS FOR FIRST RESUME --------
        if uploaded_file == uploaded_files[0]:

            st.subheader("📃 Extracted Resume Text")
            st.text_area("Resume Content", resume_text[:1000])

            st.subheader("💡 Detected Skills")

            if detected_skills:
                st.success(", ".join(detected_skills))
            else:
                st.warning("No skills detected")

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

            # -------- ROLE MATCHING --------
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

            # -------- DASHBOARD METRICS --------
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Resume Strength Score")
                st.progress(resume_score)
                st.write(f"Score: {resume_score}/100")

            with col2:
                st.subheader("📈 Job Match Score")
                st.progress(match_percent)
                st.write(f"Match Percentage: {match_percent}%")

            # -------- MISSING SKILLS --------
            st.subheader("⚠ Missing Skills")

            if missing_skills:
                st.warning(", ".join(missing_skills))
            else:
                st.success("Your resume matches this role well!")

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
# ---------------- CANDIDATE RANKING ----------------

if ranking_results:

    st.subheader("🏆 Candidate Ranking")

    # Sort candidates by score (highest first)
    ranking_results = sorted(ranking_results, key=lambda x: x[1], reverse=True)

    jd_skills = []

    for skill in skills_list:
        if job_description and skill in job_description.lower():
            jd_skills.append(skill)

    total_jd_skills = len(jd_skills)

    for i, (name, score) in enumerate(ranking_results):

        if total_jd_skills > 0:
            percentage = int((score / total_jd_skills) * 100)
        else:
            percentage = 0

        st.metric(
            label=f"🏅 Rank #{i+1}",
            value=f"{percentage}% match",
            delta=name
        )

        st.progress(percentage/100)

        if percentage > 80:
            st.success("Excellent Fit")

        elif percentage > 50:
            st.info("Good Fit")

        else:
            st.warning("Low Fit")
