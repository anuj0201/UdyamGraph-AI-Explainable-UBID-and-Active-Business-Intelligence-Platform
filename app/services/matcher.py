from rapidfuzz import fuzz
from app.utils.text_cleaning import normalize_text


# =========================================
# COMPUTE SIMILARITY
# =========================================
def compute_similarity(r1, r2):

    reasons = []

    # ---------------------------------
    # PAN MATCH
    # ---------------------------------
    pan_score = 0

    if r1.pan and r2.pan:

        if r1.pan.strip().upper() == r2.pan.strip().upper():

            pan_score = 1

            reasons.append("PAN matched")

        else:

            reasons.append("PAN mismatch")

    else:

        reasons.append("PAN missing")

    # ---------------------------------
    # GSTIN MATCH
    # ---------------------------------
    gstin_score = 0

    if r1.gstin and r2.gstin:

        if (
            r1.gstin.strip().upper() ==
            r2.gstin.strip().upper()
        ):

            gstin_score = 1

            reasons.append("GSTIN matched")

        else:

            reasons.append("GSTIN mismatch")

    else:

        reasons.append("GSTIN missing")

    # ---------------------------------
    # NAME SIMILARITY
    # ---------------------------------
    try:

        name_score = fuzz.token_sort_ratio(
            normalize_text(r1.name or ""),
            normalize_text(r2.name or "")
        ) / 100

    except Exception:

        name_score = 0

    if name_score > 0.8:

        reasons.append(
            f"High name similarity ({name_score:.2f})"
        )

    elif name_score > 0.5:

        reasons.append(
            f"Moderate name similarity ({name_score:.2f})"
        )

    else:

        reasons.append(
            f"Low name similarity ({name_score:.2f})"
        )

    # ---------------------------------
    # ADDRESS SIMILARITY
    # ---------------------------------
    try:

        address_score = fuzz.token_sort_ratio(
            normalize_text(r1.address or ""),
            normalize_text(r2.address or "")
        ) / 100

    except Exception:

        address_score = 0

    if address_score > 0.8:

        reasons.append(
            f"High address similarity ({address_score:.2f})"
        )

    elif address_score > 0.5:

        reasons.append(
            f"Moderate address similarity ({address_score:.2f})"
        )

    else:

        reasons.append(
            f"Low address similarity ({address_score:.2f})"
        )

    # ---------------------------------
    # PHONE MATCH
    # ---------------------------------
    phone_score = 0

    if r1.phone and r2.phone:

        if (
            str(r1.phone).strip() ==
            str(r2.phone).strip()
        ):

            phone_score = 1

            reasons.append("Phone matched")

        else:

            reasons.append("Phone mismatch")

    else:

        reasons.append("Phone missing")

    # ---------------------------------
    # FINAL SCORE
    # ---------------------------------
    final_score = (
        (0.30 * pan_score) +
        (0.20 * gstin_score) +
        (0.25 * name_score) +
        (0.15 * address_score) +
        (0.10 * phone_score)
    )

    final_score = round(final_score, 2)

    # ---------------------------------
    # DECISION LOGIC
    # ---------------------------------
    if final_score >= 0.85:

        decision = "auto_merge"

    elif final_score >= 0.60:

        decision = "review"

    else:

        decision = "new_entity"

        reasons.append(
            "Overall similarity too low"
        )

    # IMPORTANT:
    # routes.py expects:
    # score, decision, reasons
    return final_score, decision, reasons


# =========================================
# GENERATE REASONS
# =========================================
def generate_reasons(reasons):

    if not reasons:

        return "No matching reasons"

    return ", ".join(reasons)