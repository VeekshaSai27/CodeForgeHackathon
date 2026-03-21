from skill_extractor import extract_skills_from_text
from feature_engineering import compute_features
from model import train_model, compute_scores
from utils import load_text

# Load files
resume_text = load_text("data/resume.txt")
jd_text = load_text("data/jd.txt")

print("Extracting skills using LLM...")

resume_skills = extract_skills_from_text(resume_text, mode="resume")
jd_skills = extract_skills_from_text(jd_text, mode="jd")

print("\nResume Skills:", resume_skills)
print("JD Skills:", jd_skills)

data = compute_features(resume_skills, jd_skills)

model, scaler, df = train_model(data)

df_ranked = compute_scores(df, model)

print("\n🔥 Top Skills to Learn:\n")
print(df_ranked[["skill", "score"]].head(10))