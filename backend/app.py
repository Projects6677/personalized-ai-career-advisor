
---

## `backend/app.py`
```py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.recommend import RecommendationService
import uvicorn
import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"

app = FastAPI(title="Personalized AI Career Advisor (MVP)")

# load sample catalog
with open(DATA_DIR / "roles_skills.json", "r", encoding="utf-8") as f:
    ROLE_CATALOG = json.load(f)

rec_service = RecommendationService(role_catalog=ROLE_CATALOG)

class OnboardPayload(BaseModel):
    student_id: str
    age: Optional[int]
    location: Optional[str]
    education: Optional[dict]
    languages: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    aptitude_scores: Optional[dict] = {}
    projects: Optional[List[dict]] = []
    constraints: Optional[dict] = {}

class RecommendRequest(BaseModel):
    student_profile: OnboardPayload
    top_k: Optional[int] = 3

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/onboard")
def onboard(payload: OnboardPayload):
    # For MVP we just echo back and store in sample file (demo only)
    sample_profiles_path = DATA_DIR / "sample_profiles.json"
    try:
        profiles = []
        if sample_profiles_path.exists():
            with open(sample_profiles_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        # replace if exists
        profiles = [p for p in profiles if p.get("student_id") != payload.student_id]
        profiles.append(payload.dict())
        with open(sample_profiles_path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "onboarded", "student_id": payload.student_id}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    student = req.student_profile.dict()
    top_k = req.top_k or 3
    recs = rec_service.recommend(student_profile=student, top_k=top_k)
    return {"student_id": student.get("student_id"), "recommendations": recs}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
