import streamlit as st
from utils import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from skills import skills_list
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from groq import Groq
import os

# ---------------- GROQ CLIENT ----------------
client = Groq(api_key="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")

# ---------------- JOB ROLE DATABASE ----------------
job_roles = {
    "Data Scientist": [
        "python","machine learning","deep learning","nlp","sql","statistics"
    ],
    "Data Analyst": [
        "python","sql","excel","tableau","power bi","data visualization"
    ],
    "ML Engineer": [
        "python","tensorflow","pytorch","machine learning","deep learning"
    ]
}

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄")

st.title("🚀 AI Resume Analyzer PRO")
st.write("Upload your resume and get detailed analysis")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Resume (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:

    # -------- EXTRACT TEXT --------
    file_type = uploaded_file.name.split(".")[-1]

    if file_type == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)

    elif file_type == "docx":
        resume_text = extract_text_from_docx(uploaded_file)

    elif file_type == "txt":
        resume_text = extract_text_from_txt(uploaded_file)

    # -------- SHOW TEXT --------
    st.subheader("📃 Extracted Resume Text")
    st.text_area("Resume Content", resume_text[:1000])

    # -------- SKILL DETECTION --------
    detected_skills = []

    for skill in skills_list:
        if skill in resume_text:
            detected_skills.append(skill)

    st.subheader("💡 Detected Skills")

    if detected_skills:
        st.success(", ".join(detected_skills))
    else:
        st.warning("No skills detected")

    # -------- RESUME SCORE --------
    score = 0

    score += len(detected_skills) * 5

    if "projects" in resume_text:
        score += 20

    if "experience" in resume_text:
        score += 20

    if "education" in resume_text:
        score += 10

    score = min(score,100)

    st.subheader("📊 Resume Strength Score")
    st.progress(score)
    st.write(f"Resume Score: {score}/100")

    # -------- JOB ROLE MATCH --------
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

    match_percent = int(((len(required_skills)-len(missing_skills)) / len(required_skills))*100)

    st.subheader("📈 Job Match Score")
    st.progress(match_percent)
    st.write(f"Match Percentage: {match_percent}%")

    # -------- MISSING SKILLS --------
    st.subheader("⚠ Missing Skills")

    if missing_skills:
        st.warning(", ".join(missing_skills))
    else:
        st.success("Your resume matches this role well!")

    # -------- SECTION CHECK --------
    sections = ["education","skills","projects","experience"]

    missing_sections = []

    for section in sections:
        if section not in resume_text:
            missing_sections.append(section)

    st.subheader("📑 Resume Section Analysis")

    if missing_sections:
        st.warning("Missing sections: " + ", ".join(missing_sections))
    else:
        st.success("All important sections found")

    # -------- SUGGESTIONS --------
    st.subheader("🛠 Suggestions")

    if score < 40:
        st.warning("Add more technical skills and projects.")
    elif score < 70:
        st.info("Good resume, but adding certifications could help.")
    else:
        st.success("Strong resume!")

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
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        feedback = response.choices[0].message.content

        st.write(feedback)