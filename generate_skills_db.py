import json

skills_data = {

"programming_languages":[
"python","java","c","c++","c#","javascript","typescript","go","rust","ruby","php","kotlin","swift","scala"
],

"machine_learning":[
"machine learning","deep learning","nlp","computer vision","reinforcement learning",
"transformers","huggingface","langchain","prompt engineering","generative ai"
],

"ml_libraries":[
"tensorflow","keras","pytorch","scikit-learn","xgboost","lightgbm","catboost"
],

"data_science":[
"pandas","numpy","scipy","matplotlib","seaborn","plotly","statsmodels"
],

"databases":[
"sql","mysql","postgresql","mongodb","oracle","redis","cassandra","sqlite"
],

"big_data":[
"hadoop","spark","pyspark","hive","kafka","hbase"
],

"web_development":[
"html","css","bootstrap","react","angular","vue","node.js","express","django","flask","fastapi"
],

"cloud":[
"aws","amazon web services","azure","gcp","google cloud","cloud computing"
],

"devops":[
"docker","kubernetes","jenkins","ci/cd","terraform","ansible"
],

"data_visualization":[
"tableau","power bi","looker"
],

"mobile":[
"android","ios","flutter","react native"
],

"cybersecurity":[
"penetration testing","ethical hacking","network security","cryptography","information security"
],

"tools":[
"streamlit","gradio","jupyter","colab","linux","bash","shell scripting"
],

"soft_skills":[
"communication","teamwork","leadership","problem solving","critical thinking",
"time management","adaptability","creativity"
]

}

# expand skills to create a larger database

expanded_skills = {}

for category, skills in skills_data.items():

    expanded = []

    for skill in skills:

        expanded.append(skill)
        expanded.append(f"{skill} development")
        expanded.append(f"{skill} framework")
        expanded.append(f"{skill} tools")

    expanded_skills[category] = expanded

# save JSON

with open("skills_database.json","w") as f:
    json.dump(expanded_skills,f,indent=4)

print("Skills database generated successfully!")