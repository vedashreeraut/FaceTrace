import os
import json
from urllib.parse import (
    urlparse,
    urlunparse,
    parse_qsl,
    urlencode,
)

import requests
import serpapi
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY"
)

INPUT_IMAGE = "input/face.jpg"

OUTPUT_FILE = (
    "output/search_results.json"
)


SOCIAL_PLATFORMS = {

    "instagram.com": "Instagram",

    "x.com": "X",

    "twitter.com": "X",

    "facebook.com": "Facebook",

    "tiktok.com": "TikTok",

    "reddit.com": "Reddit",

    "youtube.com": "YouTube",
}


# Obvious indicators that the content is no longer available.
DEAD_CONTENT_MARKERS = {

    "this post was deleted",

    "this post has been deleted",

    "post was deleted",

    "post has been deleted",

    "this post was removed",

    "post was removed",

    "this content is no longer available",

    "content is no longer available",

    "page not found",

    "video unavailable",

    "video has been removed",

    "account suspended",

    "account has been suspended",

    "[deleted]",

    "[removed]",
}


# Tracking parameters that don't identify a different page.
TRACKING_PARAMETERS = {

    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "igshid",
}


# ============================================================
# PLATFORM
# ============================================================

def get_platform(url):

    try:

        hostname = (
            urlparse(url)
            .hostname
        )

        if not hostname:
            return None

        hostname = (
            hostname
            .lower()
            .removeprefix("www.")
        )

        for domain, platform in SOCIAL_PLATFORMS.items():

            if (
                hostname == domain
                or hostname.endswith(
                    "." + domain
                )
            ):

                return platform

        return None

    except Exception:

        return None


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url):

    try:

        parsed = urlparse(url)

        filtered_query = [

            (key, value)

            for key, value
            in parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )

            if key.lower()
            not in TRACKING_PARAMETERS
        ]


        normalized = parsed._replace(

            scheme=(
                parsed.scheme
                or "https"
            ).lower(),

            netloc=(
                parsed.netloc
                .lower()
            ),

            query=urlencode(
                filtered_query
            ),

            fragment="",
        )


        result = urlunparse(
            normalized
        )


        # Remove a trailing slash from non-root paths.
        if (
            result.endswith("/")
            and
            parsed.path not in {
                "",
                "/",
            }
        ):

            result = result[:-1]


        return result

    except Exception:

        return url


# ============================================================
# DEAD CONTENT DETECTION
# ============================================================

def contains_dead_marker(text):

    if not text:
        return False


    normalized = str(
        text
    ).lower()


    return any(
        marker in normalized
        for marker in DEAD_CONTENT_MARKERS
    )


def looks_deleted_or_unavailable(match):

    fields = [

        match.get(
            "title",
            ""
        ),

        match.get(
            "snippet",
            ""
        ),

        match.get(
            "description",
            ""
        ),

        match.get(
            "source",
            ""
        ),
    ]


    combined = " ".join(
        str(field)
        for field in fields
        if field
    )


    return contains_dead_marker(
        combined
    )


# ============================================================
# LIGHTWEIGHT URL VALIDATION
# ============================================================

def check_url_status(url):

    """
    Returns:

        True  = definitely reachable
        False = definitely unavailable
        None  = unknown / blocked / inconclusive

    We intentionally treat 403/429 as unknown rather than
    deleting legitimate pages that simply block automated requests.
    """

    headers = {

        "User-Agent":
            (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"
            )
    }


    try:

        response = requests.head(

            url,

            headers=headers,

            timeout=3,

            allow_redirects=True,
        )


        if response.status_code in {
            404,
            410,
        }:

            return False


        if (
            200
            <= response.status_code
            < 400
        ):

            return True


        if response.status_code in {
            403,
            429,
            451,
        }:

            return None


        # Some websites don't implement HEAD properly.
        if response.status_code in {
            405,
            500,
            501,
            502,
            503,
        }:

            try:

                response = requests.get(

                    url,

                    headers=headers,

                    timeout=3,

                    allow_redirects=True,

                    stream=True,
                )


                if response.status_code in {
                    404,
                    410,
                }:

                    return False


                if (
                    200
                    <= response.status_code
                    < 400
                ):

                    return True


            except requests.RequestException:

                return None


        return None


    except requests.RequestException:

        return None


# ============================================================
# CLEAN RESULT
# ============================================================

def build_result(
    match,
    match_type,
):

    url = (
        match.get("link")
        or match.get("url")
    )


    if not url:
        return None


    platform = get_platform(
        url
    )


    if not platform:
        return None


    # Remove clearly deleted/removed content.
    if looks_deleted_or_unavailable(
        match
    ):

        return None


    normalized_url = normalize_url(
        url
    )


    return {

        "platform":
            platform,

        "title":
            match.get(
                "title",
                "Untitled"
            ),

        "source":
            match.get(
                "source",
                platform
            ),

        "url":
            normalized_url,

        "thumbnail":
            match.get(
                "thumbnail"
            ),

        "image":
            match.get(
                "image"
            ),

        "snippet":
            match.get(
                "snippet",
                ""
            ),

        "match_type":
            match_type,

        "position":
            match.get(
                "position",
                9999
            ),

        "link_verified":
            None,
    }


# ============================================================
# SEARCH
# ============================================================

def search_image(
    image_path
):

    if not SERPAPI_KEY:

        raise RuntimeError(
            "SERPAPI_KEY is missing from .env"
        )


    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    print()
    print("=" * 60)
    print("              FACETRACE WEB SEARCH")
    print("=" * 60)


    client = serpapi.Client(
        api_key=SERPAPI_KEY
    )


    # ========================================================
    # STEP 1 — IMAGE UPLOAD
    # ========================================================

    print()
    print("✓ Input image found")
    print("✓ Uploading image to SerpApi...")


    upload = client.upload_image(
        image_path
    )


    if "error" in upload:

        raise RuntimeError(
            f"Image upload failed: "
            f"{upload['error']}"
        )


    image_id = upload.get(
        "image_id"
    )


    if not image_id:

        raise RuntimeError(
            "No image_id returned by SerpApi."
        )


    print("✓ Image uploaded")
    print("✓ Temporary image ID received")


    # ========================================================
    # STEP 2 — VISUAL MATCHES
    # ========================================================

    print()
    print("✓ Searching Google Lens visual matches...")


    visual_response = client.search({

        "engine":
            "google_lens",

        "image_id":
            image_id,

        "type":
            "visual_matches",

        "hl":
            "en",

        "country":
            "in",
    })


    if "error" in visual_response:

        raise RuntimeError(
            "Google Lens visual search failed: "
            f"{visual_response['error']}"
        )


    visual_matches = (
        visual_response.get(
            "visual_matches",
            []
        )
    )


    print(
        f"✓ {len(visual_matches)} "
        "visual matches returned"
    )


    # ========================================================
    # STEP 3 — EXACT MATCHES
    # ========================================================

    print(
        "✓ Checking Google Lens exact matches..."
    )


    exact_matches = []


    try:

        exact_response = client.search({

            "engine":
                "google_lens",

            "image_id":
                image_id,

            "type":
                "exact_matches",

            "hl":
                "en",

            "country":
                "in",
        })


        if "error" not in exact_response:

            exact_matches = (
                exact_response.get(
                    "exact_matches",
                    []
                )
            )


    except Exception as error:

        # Exact-match search is an enhancement.
        # A failure here should NOT destroy visual search.
        print(
            f"⚠ Exact-match lookup unavailable: "
            f"{error}"
        )


    print(
        f"✓ {len(exact_matches)} "
        "exact matches returned"
    )


    # ========================================================
    # STEP 4 — CONVERT EXACT RESULTS
    # ========================================================

    exact_results = []


    for match in exact_matches:

        result = build_result(
            match,
            "Exact Match"
        )


        if result:

            exact_results.append(
                result
            )


    # ========================================================
    # STEP 5 — CONVERT VISUAL RESULTS
    # ========================================================

    visual_results = []


    for match in visual_matches:

        result = build_result(
            match,
            "Visual Match"
        )


        if result:

            visual_results.append(
                result
            )


    # ========================================================
    # STEP 6 — COMBINE + DEDUPLICATE
    # ========================================================

    combined = (

        exact_results
        +
        visual_results
    )


    unique = {}


    for result in combined:

        key = normalize_url(
            result["url"]
        )


        # Exact Match always wins if the
        # same URL appears in both lists.
        if key not in unique:

            unique[key] = result

        elif (
            result["match_type"]
            ==
            "Exact Match"
        ):

            unique[key] = result


    social_results = list(
        unique.values()
    )


    # ========================================================
    # STEP 7 — VERIFY LINKS
    # ========================================================

    print(
        "✓ Checking obvious dead links..."
    )


    for result in social_results:

        status = check_url_status(
            result["url"]
        )


        result[
            "link_verified"
        ] = status


    # Remove only links we can confidently
    # prove are dead.
    social_results = [

        result

        for result
        in social_results

        if result[
            "link_verified"
        ] is not False
    ]


    # ========================================================
    # STEP 8 — RANK
    # ========================================================

    def ranking_key(result):

        # Exact matches first.
        exact_priority = (
            0
            if result["match_type"]
            == "Exact Match"
            else 1
        )


        # Known-live links before unknown links.
        link_priority = (
            0
            if result["link_verified"] is True
            else 1
        )


        # Results with thumbnails are generally
        # more useful visually.
        thumbnail_priority = (
            0
            if result.get("thumbnail")
            else 1
        )


        position = result.get(
            "position",
            9999
        )


        return (

            exact_priority,

            link_priority,

            thumbnail_priority,

            position,
        )


    social_results.sort(
        key=ranking_key
    )


    # ========================================================
    # LIMIT OUTPUT
    # ========================================================

    social_results = (
        social_results[:20]
    )


    # ========================================================
    # SAVE
    # ========================================================

    os.makedirs(
        "output",
        exist_ok=True
    )


    output = {

        "search_engine":
            "Google Lens via SerpApi",

        "search_type":
            "exact_matches + visual_matches",

        "exact_match_count":
            len(exact_results),

        "visual_match_count":
            len(visual_results),

        "social_result_count":
            len(social_results),

        "social_results":
            social_results,
    }


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            output,

            file,

            indent=4,

            ensure_ascii=False,
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 60)
    print("              SOCIAL MEDIA RESULTS")
    print("=" * 60)


    if not social_results:

        print()
        print(
            "No usable social-media results found."
        )

    else:

        for i, result in enumerate(
            social_results,
            start=1
        ):

            print(
                f"\n{i}. "
                f"[{result['platform']}] "
                f"[{result['match_type']}]"
            )

            print(
                f"Title: {result['title']}"
            )

            print(
                f"URL: {result['url']}"
            )

            print(
                "Link status: "
                f"{result['link_verified']}"
            )


    print()
    print("✓ Results saved to:")
    print(f"  {OUTPUT_FILE}")


    return social_results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    search_image(
        INPUT_IMAGE
    )