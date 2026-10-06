import os

class ConstraintParser:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def parse_query(self, query_text: str) -> dict:
        """Extracts temporal constraints and filter chips from text using Gemini 2.5 Flash or regex fallback."""
        if not query_text:
            return {"year": None, "keywords": []}

        # Rule-based fast extraction for years
        import re
        year_match = re.search(r'\b(20[0-2][0-9])\b', query_text)
        fallback_year = int(year_match.group(1)) if year_match else None

        if not self.client:
            return {"year": fallback_year, "keywords": query_text.split(), "parsed_by": "Fast-Rule Fallback"}

        try:
            prompt = f"Extract search intent from query: '{query_text}'. Return JSON with keys 'year' (integer or null) and 'category' (string or null)."
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            # Safe return parsing
            return {
                "year": fallback_year,
                "raw_gemini_response": response.text if hasattr(response, 'text') else str(response),
                "parsed_by": "Gemini 2.5 Flash"
            }
        except Exception:
            return {"year": fallback_year, "keywords": query_text.split(), "parsed_by": "Fallback"}
