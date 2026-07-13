from pydantic import BaseModel


class WorkExperience(BaseModel):
    company: str = ""
    position: str = ""
    start_date: str = ""
    end_date: str = ""
    responsibilities: list[str] = []


class Education(BaseModel):
    school: str = ""
    degree: str = ""
    major: str = ""
    start_date: str = ""
    end_date: str = ""


class ResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    work_experience: list[WorkExperience] = []
    education: list[Education] = []
    skills: list[str] = []
    certifications: list[str] = []
    languages: list[str] = []


class JDData(BaseModel):
    job_title: str = ""
    department: str = ""
    location: str = ""
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    experience_years: str = ""
    education_requirement: str = ""
    responsibilities: list[str] = []
    keywords: list[str] = []


class SkillGap(BaseModel):
    skill: str = ""
    importance: str = "medium"
    suggestion: str = ""


class OptimizationSuggestion(BaseModel):
    section: str = ""
    original: str = ""
    improved: str = ""
    reason: str = ""


class AnalysisResult(BaseModel):
    match_score: int = 0
    match_summary: str = ""
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    skill_gaps: list[SkillGap] = []
    experience_gap: str = ""
    optimization_suggestions: list[OptimizationSuggestion] = []
    keyword_recommendations: list[str] = []
    overall_advice: str = ""
