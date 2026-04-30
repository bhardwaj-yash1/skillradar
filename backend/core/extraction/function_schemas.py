"""OpenAI tool schemas used by extraction and roadmap generation."""

from __future__ import annotations


def job_description_extraction_tool() -> dict:
    """Return the structured tool schema for JD extraction."""
    return {
        "type": "function",
        "function": {
            "name": "extract_job_requirements",
            "description": "Extract structured requirements and skills from a job description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "category": {"type": "string"},
                                "is_required": {"type": "boolean"},
                                "confidence": {"type": "number"},
                            },
                            "required": ["name", "category", "is_required", "confidence"],
                        },
                    },
                    "role_category": {"type": "string"},
                    "experience_level": {"type": "string"},
                    "domain": {"type": "string"},
                },
                "required": ["skills", "role_category", "experience_level", "domain"],
            },
        },
    }


def roadmap_generation_tool() -> dict:
    """Return a tool schema for generating roadmap phase descriptions."""
    return {
        "type": "function",
        "function": {
            "name": "generate_learning_roadmap",
            "description": "Create a phased learning roadmap for missing market skills.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "phase_title": {"type": "string"},
                                "week_range": {"type": "string"},
                                "skills": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "skill_name": {"type": "string"},
                                            "project_idea": {"type": "string"},
                                            "why_important": {"type": "string"},
                                        },
                                        "required": ["skill_name", "project_idea", "why_important"],
                                    },
                                },
                            },
                            "required": ["phase_title", "week_range", "skills"],
                        },
                    }
                },
                "required": ["phases"],
            },
        },
    }
