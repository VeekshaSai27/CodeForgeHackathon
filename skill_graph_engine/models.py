from pydantic import BaseModel, field_validator


class SkillNode(BaseModel):
    skill: str
    importance: float = 0.5
    proficiency: float = 0.0
    confidence: float = 0.0

    @field_validator("importance", "proficiency", "confidence")
    @classmethod
    def in_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Value must be between 0 and 1, got {v}")
        return v


class RoadmapItem(BaseModel):
    skill: str
    score: float
    reason: str
    prerequisites: list[str]


class LearningPath(BaseModel):
    next_skills: list[str]
    roadmap: list[RoadmapItem]
    reasoning: dict[str, str]
