"""
GenAI Explanation Layer for ScamShield AI.

This module does NOT make the fraud/spam/phishing decision. The trained
ML pipelines (job_model, sms_model, url_pipeline) remain the sole
decision-makers, exactly as evaluated in the project report.

This module's only job is: given a verdict the ML model already made,
generate a short, plain-English explanation of WHY, using an LLM.
This keeps the classification task deterministic and evaluable, while
adding a genuine generative-AI component to the system.

Provider: Groq (free tier, fast Llama 3.1 inference).
To use Gemini instead, see the GEMINI SWITCH block near the bottom.
"""

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

_client = None
_client_error = None

if GROQ_API_KEY:
    try:
        from groq import Groq

        _client = Groq(api_key=GROQ_API_KEY)
    except Exception as exc:  # library missing or bad init
        _client_error = str(exc)


SYSTEM_PROMPT = """You are the explanation module inside ScamShield AI, \
a scam and phishing detection tool.

You are given a verdict that a separate, already-trained machine \
learning model produced (job posting, SMS message, or website URL), \
along with its risk score and any rule-based indicators that were \
already detected.

Your ONLY job is to explain, in plain and reassuring language, WHY the \
input received this verdict. Rules:
- Do NOT change, soften, or override the model's verdict.
- Do NOT invent facts, indicators, or details that are not given to you.
- If no indicators were found, say so plainly rather than making some up.
- Keep the explanation to 3-4 short sentences, written for a \
  non-technical reader.
- End with one concrete, practical next step the user should take.
"""


def _build_user_prompt(module_type, input_text, prediction_label,
                        risk_score, indicators):
    indicator_text = "; ".join(indicators) if indicators else "none flagged by the rule-based checks"
    snippet = (input_text or "").strip().replace("\n", " ")[:500]

    return f"""Module: {module_type}
Model verdict: {prediction_label}
Risk score: {risk_score}/100
Rule-based indicators already found: {indicator_text}
Original input (truncated to 500 chars): "{snippet}"

Explain this result to the user in 3-4 sentences, ending with one \
practical next step."""


def generate_explanation(module_type, input_text, prediction_label,
                          risk_score, indicators):
    """
    Returns a short natural-language explanation string.

    Args:
        module_type: "Job Posting" | "SMS Message" | "Website URL"
        input_text: the raw text/URL the user submitted
        prediction_label: e.g. "Fraudulent", "Legitimate", "Spam",
                           "Likely Phishing", "Likely Legitimate"
        risk_score: numeric 0-100
        indicators: list[str] of rule-based indicators already found

    Falls back to a static, honest message if no API key is configured
    or the API call fails for any reason -- the app must never crash
    because the GenAI layer is unavailable.
    """
    if _client is None:
        if _client_error:
            return (
                "AI explanation is unavailable (Groq client failed to "
                "initialize). The risk indicators above still reflect "
                "the trained model's assessment."
            )
        return (
            "AI explanation is unavailable because no GROQ_API_KEY was "
            "found. Add one to your .env file to enable this feature. "
            "The risk indicators above still reflect the trained "
            "model's assessment."
        )

    user_prompt = _build_user_prompt(
        module_type, input_text, prediction_label, risk_score, indicators
    )

    try:
        response = _client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=220,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return (
            "AI explanation is temporarily unavailable (API request "
            "failed). The risk indicators above still reflect the "
            "trained model's assessment."
        )
        

# ============================================================
# GEMINI SWITCH
# ============================================================
# If you'd rather use Google Gemini's free tier instead of Groq:
#
#   pip install google-generativeai
#
# Replace the client setup at the top of this file with:
#
#   import google.generativeai as genai
#   genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
#   _model = genai.GenerativeModel("gemini-1.5-flash")
#
# And replace the try block inside generate_explanation with:
#
#   response = _model.generate_content(
#       f"{SYSTEM_PROMPT}\n\n{user_prompt}"
#   )
#   return response.text.strip()
#
# Everything else (fallback behavior, function signature, app.py
# integration) stays identical either way.
