"""
Recommendation service (MVP).

This file contains a small pipeline:
- vectorize roles (from catalog) using simple TF-IDF-like token hashing (toy)
- vectorize student profile (interests + projects + aptitude)
- compute cosine similarity and return top-k roles with a basic explanation + skill gaps.

Replace the embedding + similarity logic with Vertex AI embeddings + a vector DB later.
"""
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def text_from_role(role: Dict) -> str:
    # flatten role -> string for vectorization
    parts = [role.get("title", "")]
    skills = role.get("skills", [])
    desc = role.get("description", "")
    return " ".join([parts[0]] + skills + [desc])

def text_from_profile(profile: Dict) -> str:
    pieces = []
    if profile.get("interests"):
        pieces += profile["interests"]
    if profile.get("projects"):
        for p in profile["projects"]:
            pieces.append(p.get("title", ""))
            pieces += p.get("skills", [])
    # include aptitude keywords
    if profile.get("aptitude_scores"):
        for k, v in profile["aptitude_scores"].items():
            pieces.append(f"{k}:{v}")
    if profile.get("education") and isinstance(profile["education"], dict):
        pieces += list(profile["education"].values())
    return " ".join(map(str, pieces))

class RecommendationService:
    def __init__(self, role_catalog: List[Dict]):
        self.role_catalog = role_catalog
        # build vectorizer over role corpus
        corpus = [text_from_role(r) for r in role_catalog]
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=3000)
        self.role_matrix = self.vectorizer.fit_transform(corpus)
        # store ids map
        self.role_ids = [r.get("id", r.get("title")) for r in role_catalog]

    def recommend(self, student_profile: Dict, top_k: int = 3) -> List[Dict]:
        profile_text = text_from_profile(student_profile)
        profile_vec = self.vectorizer.transform([profile_text])
        sims = cosine_similarity(profile_vec, self.role_matrix).flatten()
        top_idx = sims.argsort()[::-1][:top_k]
        recs = []
        for idx in top_idx:
            role = self.role_catalog[idx]
            sim_score = float(sims[idx])
            # simple skill gap calculation
            role_skills = set([s.lower() for s in role.get("skills", [])])
            student_skills = set()
            for p in student_profile.get("projects", []):
                for sk in p.get("skills", []):
                    student_skills.add(sk.lower())
            known = list(role_skills & student_skills)
            missing = list(role_skills - student_skills)
            recs.append({
                "role_id": role.get("id", role.get("title")),
                "title": role.get("title"),
                "similarity": round(sim_score, 4),
                "why": self._why_text(student_profile, role, sim_score, known, missing),
                "known_skills": known,
                "missing_skills": missing,
                "starter_plan": self._starter_plan(role, missing)
            })
        return recs

    def _why_text(self, profile, role, sim_score, known, missing):
        reasons = []
        if profile.get("interests"):
            # if any interest appears in role title or skills
            title = role.get("title","").lower()
            for i in profile["interests"]:
                if i.lower() in title or i.lower() in " ".join(role.get("skills", [])).lower():
                    reasons.append(f"Interest in '{i}' matches role keywords.")
        # aptitude hint
        if profile.get("aptitude_scores"):
            top = sorted(profile["aptitude_scores"].items(), key=lambda x: x[1], reverse=True)[0]
            reasons.append(f"Strong aptitude in {top[0]} ({top[1]}).")
        if not reasons:
            reasons.append("Profile similarity based on projects and interests.")
        return reasons

    def _starter_plan(self, role, missing_skills):
        # simple template: learn top 3 missing skills via project-based learning
        steps = []
        if not missing_skills:
            steps.append("You already have many required skills — build a showcase project combining them.")
        else:
            for i, sk in enumerate(missing_skills[:3], start=1):
                steps.append(f"Learn **{sk}** via a short course and build a small project demonstrating it.")
            steps.append("Combine those projects into a portfolio and publish a 1-page case study.")
        return steps
