"""
Claude AI Service
Uses the Anthropic Claude API for claim story generation and feedback analysis.
Set ANTHROPIC_API_KEY in your environment or a .env file.
"""
import os

# Load .env file if present (optional dependency)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        _client = anthropic.Anthropic(api_key=api_key)
        print("[Claude] Client initialized successfully.")
    except Exception as e:
        print(f"[Claude] Failed to initialize client: {e}")
        _client = None
    return _client


# ─────────────────────────────────────────────────────────────────────────────
# Story / Description Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_claim_story(scenario: dict) -> str | None:
    """
    Use Claude to write a realistic, narrative-style claim description.
    Returns the story string, or None if Claude is unavailable.
    """
    client = _get_client()
    if client is None:
        return None

    claim_type = scenario.get("claim_type", "medical")
    difficulty  = scenario.get("difficulty", "easy")
    procedure   = scenario.get("procedure_code", "")
    diagnosis   = scenario.get("diagnosis_code", "")
    amount      = scenario.get("claim_amount", 0)
    age         = scenario.get("patient_age", 40)

    # Pull client profile details if available
    profile = scenario.get("client_profile", {})
    name        = profile.get("name", "the patient")
    policy_num  = profile.get("policy_number", "")
    coverage    = profile.get("coverage_type", "")

    # Pull document status if available
    doc_status  = scenario.get("document_status", {})
    submitted   = doc_status.get("submitted", [])
    missing     = doc_status.get("missing", [])

    # Complexity descriptor
    complexity_map = {
        "easy":   "straightforward with clear documentation",
        "medium": "moderately complex with some ambiguity",
        "hard":   "complex with potential red flags or irregularities",
    }
    complexity = complexity_map.get(difficulty, "standard")

    # Build the prompt
    if claim_type == "life":
        user_prompt = (
            f"You are writing a realistic insurance claim file note for a claims adjuster training game.\n\n"
            f"Claim type: Life Insurance Death Benefit\n"
            f"Policyholder age at death: {age}\n"
            f"Policy number: {policy_num}\n"
            f"Coverage: {coverage}\n"
            f"Claim amount: ${amount:,.0f}\n"
            f"Complexity: {complexity}\n"
            f"Documents submitted: {', '.join(submitted) if submitted else 'None listed'}\n"
            f"Documents missing: {', '.join(missing) if missing else 'None'}\n\n"
            f"Write a 2-3 paragraph claim narrative as it would appear in a real insurance claim file. "
            f"Use realistic insurance adjuster language. Describe the circumstances of the claim, "
            f"the documentation status, and any notable factors an adjuster would need to review. "
            f"Do NOT state whether the claim is valid or invalid — that is for the trainee to decide. "
            f"Do NOT include headings, labels, bullet points, or markdown. Write in flowing prose only. "
            f"Use the policyholder's name ({name}) consistently throughout."
        )
    else:
        type_label = "Medical" if claim_type == "medical" else "Dental"
        user_prompt = (
            f"You are writing a realistic insurance claim file note for a claims adjuster training game.\n\n"
            f"Claim type: {type_label} Insurance\n"
            f"Patient name: {name}\n"
            f"Patient age: {age}\n"
            f"Policy number: {policy_num}\n"
            f"Coverage: {coverage}\n"
            f"Procedure code: {procedure}\n"
            f"Diagnosis code: {diagnosis}\n"
            f"Claim amount: ${amount:,.2f}\n"
            f"Complexity: {complexity}\n"
            f"Documents submitted: {', '.join(submitted) if submitted else 'None listed'}\n"
            f"Documents missing: {', '.join(missing) if missing else 'None'}\n\n"
            f"Write a 2-3 paragraph claim narrative as it would appear in a real insurance claim file. "
            f"Use realistic insurance adjuster language. Describe the treatment or service, "
            f"the documentation status, and any notable factors an adjuster would need to review. "
            f"Do NOT state whether the claim is valid or invalid — that is for the trainee to decide. "
            f"Do NOT include headings, labels, bullet points, or markdown. Write in flowing prose only. "
            f"Use the patient's name ({name}) consistently throughout."
        )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = response.content[0].text.strip() if response.content else None
        if text and len(text) > 30:
            print(f"[Claude] Story generated ({len(text)} chars).")
            return text
        return None
    except Exception as e:
        print(f"[Claude] Story generation error: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Feedback / Analysis Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_claim_feedback(
    scenario: dict,
    user_answer: str,
    correct_answer: str,
    rule_explanation: str,
) -> str | None:
    """
    Use Claude to analyze the claim and provide educational feedback.
    Includes confidence commentary on why the answer is correct/incorrect.
    Returns a feedback string, or None if Claude is unavailable.
    """
    client = _get_client()
    if client is None:
        return None

    is_correct  = user_answer.lower() == correct_answer.lower()
    claim_type  = scenario.get("claim_type", "medical")
    difficulty  = scenario.get("difficulty", "easy")
    procedure   = scenario.get("procedure_code", "")
    diagnosis   = scenario.get("diagnosis_code", "")
    amount      = scenario.get("claim_amount", 0)
    age         = scenario.get("patient_age", 40)
    description = scenario.get("description", "")

    profile     = scenario.get("client_profile", {})
    name        = profile.get("name", "the patient")

    doc_status  = scenario.get("document_status", {})
    submitted   = doc_status.get("submitted", [])
    missing     = doc_status.get("missing", [])

    verdict = "CORRECT" if is_correct else "INCORRECT"

    user_prompt = (
        f"You are an expert insurance claims trainer giving feedback to a trainee adjuster.\n\n"
        f"=== CLAIM DETAILS ===\n"
        f"Claim type: {claim_type}\n"
        f"Patient/Policyholder: {name}, age {age}\n"
        f"Procedure code: {procedure}\n"
        f"Diagnosis code: {diagnosis}\n"
        f"Claim amount: ${amount:,.2f}\n"
        f"Difficulty: {difficulty}\n"
        f"Claim description: {description}\n"
        f"Documents submitted: {', '.join(submitted) if submitted else 'None'}\n"
        f"Documents missing: {', '.join(missing) if missing else 'None'}\n\n"
        f"=== TRAINEE ASSESSMENT ===\n"
        f"The trainee answered: {user_answer.upper()}\n"
        f"The correct answer is: {correct_answer.upper()}\n"
        f"The trainee was: {verdict}\n\n"
        f"=== KEY RULE/FINDING ===\n"
        f"{rule_explanation}\n\n"
        f"=== YOUR TASK ===\n"
        f"Write 3-4 sentences of educational feedback for the trainee. Your feedback must:\n"
        f"1. Acknowledge whether they were correct or incorrect (one sentence).\n"
        f"2. Explain the key factors in this claim that determine the correct answer.\n"
        f"3. Express your confidence (high/medium/low) that this answer is unambiguous, "
        f"   and briefly explain what made this case {'clear-cut' if difficulty == 'easy' else 'tricky' if difficulty == 'hard' else 'moderately complex'}.\n"
        f"4. Give one practical tip for spotting similar claims in the future.\n\n"
        f"Write in second person ('You...'). Be direct, professional, and educational. "
        f"Do NOT repeat these instructions. Return ONLY the feedback text."
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = response.content[0].text.strip() if response.content else None
        if text and len(text) > 20:
            print(f"[Claude] Feedback generated ({len(text)} chars).")
            return text
        return None
    except Exception as e:
        print(f"[Claude] Feedback generation error: {e}")
        return None
