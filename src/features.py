import hashlib
import json
from datetime import datetime, timezone


SOCIAL_PLATFORMS = {
    "facebook",
    "instagram",
    "x",
    "twitter",
    "reddit",
    "tiktok",
    "youtube",
    "pinterest",
    "linkedin",
    "threads",
}


def canonical_record(result: dict) -> dict:
    """
    Build the exact data representation whose fingerprint
    will be used for provenance verification.
    """

    return {
        "platform": str(
            result.get("platform", "")
        ).strip(),

        "title": str(
            result.get("title", "")
        ).strip(),

        "url": str(
            result.get("url", "")
        ).strip(),
    }


def fingerprint_record(result: dict) -> str:
    """
    Generate a deterministic SHA-256 fingerprint from the
    canonical evidence record.
    """

    record = canonical_record(result)

    canonical_json = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

def classify_match(result: dict) -> str:
    """
    Classify a search result conservatively.

    Important:
    The `exact_matches` field on a Visual Match indicates
    that exact matches exist somewhere in the Lens search.
    It does NOT mean that this individual result is exact.

    Therefore an individual result is only labeled
    "Exact Match" when web_search.py explicitly marks
    it as coming from the exact_matches result set.
    """

    match_type = str(
        result.get("match_type", "")
    ).strip().lower()

    if match_type in {
        "exact",
        "exact_match",
        "exact match",
    }:
        return "Exact Match"

    if match_type in {
        "visual",
        "visual_match",
        "visual match",
    }:
        return "Visual Match"

    return "Related Match"

def is_social_platform(result: dict) -> bool:
    """
    Check whether the result is from a social-media platform.
    """

    platform = str(
        result.get("platform", "")
    ).strip().lower()

    return platform in SOCIAL_PLATFORMS


def calculate_evidence_score(result: dict) -> dict:
    """
    Calculate an evidence-strength score.

    This score describes the quality of the discovered
    evidence. It is NOT a probability of identity.
    """

    score = 0
    reasons = []
    limitations = []

    match_type = classify_match(result)


    # ========================================================
    # 1. GOOGLE LENS MATCH TYPE
    # ========================================================

    if match_type == "Exact Match":

        score += 50

        reasons.append(
            "Returned by Google Lens Exact Matches."
        )

    elif match_type == "Visual Match":

        score += 30

        reasons.append(
            "Returned by Google Lens Visual Matches."
        )

        limitations.append(
            "This is a visual match, not a confirmed "
            "pixel-identical image."
        )

    else:

        score += 15

        reasons.append(
            "Returned as related visual content."
        )

        limitations.append(
            "This result is not classified as an exact match."
        )


    # ========================================================
    # 2. SOCIAL MEDIA SOURCE
    # ========================================================

    if is_social_platform(result):

        score += 15

        reasons.append(
            "The result comes from a recognized "
            "social-media platform."
        )


    # ========================================================
    # 3. RESULT POSITION
    # ========================================================

    position = result.get(
        "position"
    )


    try:

        position = int(position)

    except (
        TypeError,
        ValueError
    ):

        position = 999


    if position <= 3:

        score += 20

        reasons.append(
            "The result appears among Google Lens's "
            "top three visual matches."
        )

    elif position <= 6:

        score += 15

        reasons.append(
            "The result appears near the top of "
            "Google Lens's visual matches."
        )

    elif position <= 10:

        score += 10

        reasons.append(
            "The result appears within the first "
            "ten Google Lens visual matches."
        )

    elif position <= 20:

        score += 5

        reasons.append(
            "The result appears within the first "
            "twenty Google Lens visual matches."
        )

    else:

        limitations.append(
            "This result appears lower in the "
            "Google Lens results."
        )


    # ========================================================
    # 4. DIRECT CONTENT VS PROFILE PAGE
    # ========================================================

    url = str(
        result.get(
            "url",
            ""
        )
    ).lower()


    direct_content = False
    profile_page = False


    if "instagram.com" in url:

        if "/p/" in url or "/reel/" in url:

            direct_content = True

        elif "/@" in url or "/accounts/" in url:

            profile_page = True


    elif (
        "facebook.com" in url
    ):

        if (
            "/posts/" in url
            or "/photos/" in url
            or "/videos/" in url
            or "/reel/" in url
        ):

            direct_content = True

        elif "/p/" in url:

            profile_page = True


    elif (
        "reddit.com" in url
    ):

        if "/comments/" in url:

            direct_content = True

        elif "/user/" in url:

            profile_page = True


    elif (
        "tiktok.com" in url
    ):

        if "/video/" in url:

            direct_content = True

        elif "/@" in url and "/video/" not in url:

            profile_page = True


    elif (
        "youtube.com" in url
    ):

        if (
            "/watch?"
            in url
            or "/shorts/" in url
        ):

            direct_content = True


    elif (
        "x.com" in url
        or "twitter.com" in url
    ):

        if "/status/" in url:

            direct_content = True

        elif "/status/" not in url:

            profile_page = True


    if direct_content:

        score += 10

        reasons.append(
            "The URL points directly to a post, "
            "photo, video, or other content item."
        )

    elif profile_page:

        score -= 5

        limitations.append(
            "This appears to be a profile page rather "
            "than a specific social-media post."
        )


    # ========================================================
    # 5. LIVE LINK
    # ========================================================

    if result.get(
        "link_verified"
    ) is True:

        score += 5

        reasons.append(
            "The source URL responded successfully "
            "to the availability check."
        )

    elif result.get(
        "link_verified"
    ) is False:

        limitations.append(
            "The source URL was identified as unavailable."
        )


    # ========================================================
    # 6. IMAGE
    # ========================================================

    if (
        result.get("thumbnail")
        or result.get("image")
    ):

        score += 5

        reasons.append(
            "The search result contains associated image data."
        )


    # ========================================================
    # 7. TITLE / METADATA
    # ========================================================

    if result.get(
        "title"
    ):

        score += 5

        reasons.append(
            "Descriptive result metadata is available."
        )


    # ========================================================
    # NORMALIZE
    # ========================================================

    score = max(
        0,
        min(
            score,
            100
        )
    )


    # ========================================================
    # EVIDENCE LEVEL
    # ========================================================

    if score >= 85:

        level = "High"

    elif score >= 65:

        level = "Moderate"

    else:

        level = "Low"


    return {

        "score":
            score,

        "level":
            level,

        "match_type":
            match_type,

        "reasons":
            reasons,

        "limitations":
            limitations,

    }
def build_evidence_record(result: dict) -> dict:
    """
    Build the complete provenance record used by the UI.
    """

    evidence = calculate_evidence_score(
        result
    )

    fingerprint = fingerprint_record(
        result
    )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()


    return {
        "platform": result.get(
            "platform",
            "Unknown"
        ),

        "title": result.get(
            "title",
            ""
        ),

        "url": result.get(
            "url",
            result.get("link", "")
        ),

        "source": result.get(
            "source",
            ""
        ),

        "thumbnail": result.get(
            "thumbnail"
        ),

        "match_type": evidence[
            "match_type"
        ],

        "evidence_score": evidence[
            "score"
        ],

        "evidence_level": evidence[
            "level"
        ],

        "why": evidence[
            "reasons"
        ],

        "limitations": evidence[
            "limitations"
        ],

        "discovered_at": timestamp,

        "sha256": fingerprint,
    }