from pydantic import BaseModel, field_validator


class SkillDNA(BaseModel):
    skills: list[str]
    importance: dict[str, float]
    confidence: dict[str, float]

    @field_validator("importance", "confidence")
    @classmethod
    def scores_in_range(cls, v: dict[str, float]) -> dict[str, float]:
        for skill, score in v.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Score for '{skill}' must be between 0 and 1, got {score}")
        return v
