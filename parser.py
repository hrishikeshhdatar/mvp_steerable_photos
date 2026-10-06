import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel

class ConstraintChips(BaseModel):
    visual_descriptors: list[str]
    active_year: int | None = None
    negative_filters: list[str] = []

SYSTEM_INSTRUCTION = """
You are a search query parser for a photo retrieval system. 
Extract structured search constraints from user follow-up text prompts.
Maintain previously established constraints unless the user explicitly contradicts or removes them.
Output must conform to the specified JSON schema.
"""

class FollowupQueryParser:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def parse_followup(self, current_prompt: str, followup_text: str, current_year: int = None) -> ConstraintChips:
        if not self.client:
            # Fallback if API key is not configured
            descriptors = [d.strip() for d in f"{current_prompt} {followup_text}".split() if len(d.strip()) > 3]
            return ConstraintChips(visual_descriptors=list(set(descriptors)), active_year=current_year)

        prompt = f"""
        Current Active Search Prompt: "{current_prompt}"
        Current Active Year Filter: {current_year}
        User Follow-up Input: "{followup_text}"

        Update the visual descriptors and active year based on the follow-up.
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=ConstraintChips,
                temperature=0.1
            ),
        )

        return ConstraintChips.model_validate_json(response.text)
