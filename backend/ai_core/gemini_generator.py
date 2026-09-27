import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiDocumentGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add it to the .env file."
            )

        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-1.5-pro"
        )

        self.client = genai.Client(api_key=api_key)

    def build_prompt(
        self,
        document_type,
        parties,
        terms,
        effective_date
    ):
        return f"""
You are a professional legal-document drafting assistant.

Create a professional draft of this legal document.

Document type: {document_type}
Parties: {parties}
Effective date: {effective_date}
Important terms: {terms}

Requirements:
- Use only information supplied by the user.
- Do not invent names, dates, addresses, amounts, laws, or other facts.
- If important information is missing, use [TO BE PROVIDED].
- Organize the document with a title, sections, clauses, and signature blocks where appropriate.
- Include all important terms supplied by the user.
- Make the draft clear, professional, and editable.
- End with a short statement that the output is an AI-generated draft
  and should be reviewed by a qualified legal professional before use.
"""

    def generate_document(
        self,
        document_type,
        parties,
        terms,
        effective_date
    ):
        prompt = self.build_prompt(
            document_type,
            parties,
            terms,
            effective_date
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        text = getattr(response, "text", None)

        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return text