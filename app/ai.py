import json
import re
from openai import OpenAI

from app.config import POE_API_KEY, POE_BASE_URL, POE_MODEL
from app.prompt import SYSTEM_PROMPT
from app.schemas import LatexResponse

client = OpenAI(
    api_key=POE_API_KEY,
    base_url=POE_BASE_URL,
)


def normalize_latex(expr: str) -> str:
    if not expr:
        return ""

    expr = expr.strip()

    # Remove markdown code fences
    expr = re.sub(r"^```(?:latex)?\s*", "", expr)
    expr = re.sub(r"\s*```$", "", expr)
    expr = expr.strip()

    # Strip common math delimiters
    if expr.startswith("$$") and expr.endswith("$$"):
        expr = expr[2:-2].strip()

    if expr.startswith(r"\[") and expr.endswith(r"\]"):
        expr = expr[2:-2].strip()

    if expr.startswith(r"\(") and expr.endswith(r"\)"):
        expr = expr[2:-2].strip()

    # Strip common display environments
    env_patterns = [
        r"^\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}$",
        r"^\\begin\{align\*?\}(.*?)\\end\{align\*?\}$",
        r"^\\begin\{gather\*?\}(.*?)\\end\{gather\*?\}$",
        r"^\\begin\{multline\*?\}(.*?)\\end\{multline\*?\}$",
        r"^\\begin\{displaymath\}(.*?)\\end\{displaymath\}$",
    ]

    for pattern in env_patterns:
        match = re.match(pattern, expr, flags=re.DOTALL)
        if match:
            expr = match.group(1).strip()
            break

    # Remove common prose prefixes
    prefixes = [
        "here is the latex:",
        "latex:",
        "rendered latex:",
        "the latex is:",
        "the expression is:",
    ]

    lowered = expr.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            expr = expr[len(prefix):].strip()
            break

    return expr.strip()


def _normalize_payload(data: dict) -> dict:
    warnings = data.get("warnings", [])
    if isinstance(warnings, str):
        warnings = [warnings] if warnings.strip() else []
    elif warnings is None:
        warnings = []
    elif not isinstance(warnings, list):
        warnings = [str(warnings)]

    data["warnings"] = warnings
    data.setdefault("intent", "generate")
    data.setdefault("latex", "")
    data.setdefault("display_mode", "block")
    data.setdefault("explanation", "")

    data["latex"] = normalize_latex(data["latex"])

    if data["display_mode"] not in ("inline", "block"):
        data["display_mode"] = "block"

    if data["intent"] not in ("generate", "fix", "explain", "convert"):
        data["intent"] = "generate"

    return data


def _extract_with_regex(content: str) -> dict:
    """
    Fallback parser for model outputs that look like JSON but contain invalid
    JSON escaping inside the latex field.
    """

    def extract_string_field(name: str, default: str = "") -> str:
        pattern = rf'"{name}"\s*:\s*"(.*?)"(?=\s*,\s*"|\s*}})'
        match = re.search(pattern, content, flags=re.DOTALL)
        if not match:
            return default
        value = match.group(1)
        value = value.replace('\\"', '"')
        return value.strip()

    intent = extract_string_field("intent", "generate")
    latex = extract_string_field("latex", "")
    display_mode = extract_string_field("display_mode", "block")
    explanation = extract_string_field("explanation", "")

    warnings = []
    warnings_match = re.search(r'"warnings"\s*:\s*(\[[^\]]*\])', content, flags=re.DOTALL)
    if warnings_match:
        raw_warnings = warnings_match.group(1)
        try:
            warnings = json.loads(raw_warnings)
        except Exception:
            warnings = []

    return {
        "intent": intent,
        "latex": latex,
        "display_mode": display_mode,
        "explanation": explanation,
        "warnings": warnings,
    }


def _extract_json(content: str) -> dict:
    content = content.strip()

    # Try direct JSON parse first
    try:
        return json.loads(content)
    except Exception:
        pass

    # Try extracting the first JSON object
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = content[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            return _extract_with_regex(candidate)

    # Last resort: regex extraction from full content
    return _extract_with_regex(content)


def generate_latex_response(user_message: str) -> LatexResponse:
    completion = client.chat.completions.create(
        model=POE_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    content = completion.choices[0].message.content or ""
    print("RAW MODEL CONTENT:", repr(content))

    try:
        parsed = _extract_json(content)
        normalized = _normalize_payload(parsed)
        print("NORMALIZED LATEX:", repr(normalized.get("latex", "")))
        return LatexResponse(**normalized)
    except Exception as e:
        raise ValueError(
            f"Failed to parse model response as LatexResponse. Raw output: {content}"
        ) from e