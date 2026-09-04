import os
import tempfile
import hashlib
from urllib.parse import quote

import streamlit as st
import face_recognition
from PIL import Image

from web_search import search_image


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FaceTrace",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "analysis_done": False,
    "search_results": [],
    "face_detected": False,
    "face_encoding_generated": False,
    "selected_result_index": 0,
    "fingerprint": None,
    "uploaded_signature": None,
}

for key, default in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = default


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 17px;
        color: #777;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 25px;
    }

    .hash-box {
        background: #f4f4f4;
        padding: 15px;
        border-radius: 8px;
        font-family: monospace;
        word-break: break-all;
    }

    .selected-box {
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #222;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔎 FaceTrace</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Face Identification • Reverse Image Search • Blockchain Verification'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Pipeline")

    st.write("1. Face identification")
    st.write("2. Reverse image search")
    st.write("3. Social-media filtering")
    st.write("4. SHA-256 fingerprint")
    st.write("5. Stellar Testnet verification")

    st.divider()

    st.caption("Search: Google Lens via SerpApi")
    st.caption("Blockchain: Stellar Testnet")


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a face image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload an image containing one face."
)


if uploaded_file:

    # --------------------------------------------------------
    # Detect whether this is a new uploaded image
    # --------------------------------------------------------

    uploaded_signature = (
        uploaded_file.name,
        uploaded_file.size
    )

    if (
        st.session_state.uploaded_signature is not None
        and
        uploaded_signature !=
        st.session_state.uploaded_signature
    ):

        # New image → clear previous analysis
        st.session_state.analysis_done = False
        st.session_state.search_results = []
        st.session_state.face_detected = False
        st.session_state.face_encoding_generated = False
        st.session_state.selected_result_index = 0
        st.session_state.fingerprint = None


    st.session_state.uploaded_signature = (
        uploaded_signature
    )


    # --------------------------------------------------------
    # Display uploaded image
    # --------------------------------------------------------

    left, right = st.columns([1, 1])


    with left:

        st.subheader("Uploaded Image")

        st.image(
            uploaded_file,
            use_container_width=True
        )


    with right:

        st.subheader("Face Identification")

        analyze_clicked = st.button(
            "🔍 Analyze Image",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # RUN ANALYSIS ONLY WHEN BUTTON IS CLICKED
    # ========================================================

    if analyze_clicked:

        try:

            # ------------------------------------------------
            # Save image temporarily
            # ------------------------------------------------

            image_bytes = uploaded_file.getvalue()

            suffix = os.path.splitext(
                uploaded_file.name
            )[1].lower()

            if suffix not in [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]:
                suffix = ".jpg"


            # ------------------------------------------------
            # Prepare image for SerpApi
            #
            # SerpApi's image upload has a 500 KB limit.
            # We keep the working copy <= ~450 KB.
            # ------------------------------------------------

            image = Image.open(
                uploaded_file
            ).convert("RGB")


            max_dimension = 1600

            image.thumbnail(
                (max_dimension, max_dimension)
            )


            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".jpg"
            )

            temp_path = temp_file.name

            temp_file.close()


            quality = 90

            while quality >= 40:

                image.save(
                    temp_path,
                    format="JPEG",
                    quality=quality,
                    optimize=True
                )

                if os.path.getsize(temp_path) <= 450_000:
                    break

                quality -= 5


            image_path = temp_path


            # =================================================
            # FACE IDENTIFICATION
            # =================================================

            st.session_state.face_detected = False
            st.session_state.face_encoding_generated = False


            st.divider()

            st.markdown(
                '<div class="section-title">'
                '1. Face Identification'
                '</div>',
                unsafe_allow_html=True
            )


            cv_image = face_recognition.load_image_file(
                image_path
            )


            face_locations = (
                face_recognition.face_locations(
                    cv_image
                )
            )


            if len(face_locations) == 0:

                st.error(
                    "❌ No face detected."
                )

                os.unlink(image_path)

                st.stop()


            if len(face_locations) > 1:

                st.warning(
                    f"{len(face_locations)} faces detected. "
                    "Please upload an image containing one face."
                )

                os.unlink(image_path)

                st.stop()


            encodings = (
                face_recognition.face_encodings(
                    cv_image,
                    face_locations
                )
            )


            if not encodings:

                st.error(
                    "Face detected, but encoding failed."
                )

                os.unlink(image_path)

                st.stop()


            st.session_state.face_detected = True
            st.session_state.face_encoding_generated = True


            st.success(
                "✓ Face detected"
            )

            st.success(
                "✓ 128-dimensional face encoding generated"
            )


            # =================================================
            # REVERSE IMAGE SEARCH
            # =================================================

            st.divider()

            st.markdown(
                '<div class="section-title">'
                '2. Reverse Image Search'
                '</div>',
                unsafe_allow_html=True
            )


            with st.spinner(
                "Searching Google Lens..."
            ):

                results = search_image(
                    image_path
                )


            os.unlink(image_path)


            st.session_state.search_results = results
            st.session_state.analysis_done = True
            st.session_state.selected_result_index = 0


            st.success(
                "✓ Genuine Google Lens search completed"
            )


        except Exception as error:

            if (
                "image_path" in locals()
                and os.path.exists(image_path)
            ):
                os.unlink(image_path)

            st.error(
                f"Analysis failed: {error}"
            )

            st.stop()


# ============================================================
# PERSISTED ANALYSIS RESULTS
# ============================================================

if st.session_state.analysis_done:

    results = st.session_state.search_results


    # ========================================================
    # FACE STATUS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '1. Face Identification'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.face_detected:

        st.success(
            "✓ Face detected"
        )

    if st.session_state.face_encoding_generated:

        st.success(
            "✓ 128-dimensional face encoding generated"
        )


    # ========================================================
    # SEARCH STATUS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '2. Reverse Image Search'
        '</div>',
        unsafe_allow_html=True
    )

    st.success(
        "✓ Google Lens search completed"
    )

    st.info(
        f"{len(results)} social-media result(s) found."
    )


    # ========================================================
    # SOCIAL MEDIA RESULTS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '3. Social Media Results'
        '</div>',
        unsafe_allow_html=True
    )


    if not results:

        st.warning(
            "No social-media matches were found."
        )

        st.stop()


    # --------------------------------------------------------
    # RESULT SELECTOR
    # --------------------------------------------------------

    result_labels = []

    for index, result in enumerate(results):

        platform = result.get(
            "platform",
            "Social Media"
        )

        title = result.get(
            "title",
            "Untitled"
        )

        # Keep radio labels reasonably readable
        if len(title) > 110:
            title = title[:110] + "..."

        result_labels.append(
            f"{index + 1}. {platform} — {title}"
        )


    selected_index = st.radio(
        "Select a result to verify on the blockchain",
        options=range(len(results)),
        format_func=lambda index:
            result_labels[index],
        key="selected_result_index"
    )


    selected_result = results[selected_index]


    # --------------------------------------------------------
    # SELECTED RESULT CARD
    # --------------------------------------------------------

    st.markdown(
        '<div class="selected-box">',
        unsafe_allow_html=True
    )

    st.subheader(
        selected_result.get(
            "title",
            "Untitled"
        )
    )

    st.write(
        f"**Platform:** "
        f"{selected_result.get('platform', 'Social Media')}"
    )

    st.write(
        f"**Source:** "
        f"{selected_result.get('source', '')}"
    )

    st.write(
        f"**URL:** "
        f"{selected_result.get('url', '')}"
    )

    if selected_result.get("thumbnail"):

        st.image(
            selected_result["thumbnail"],
            width=280
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # VIEW ORIGINAL POST
    # --------------------------------------------------------

    if selected_result.get("url"):

        st.link_button(
            "↗ View Original Post",
            selected_result["url"]
        )


    # ========================================================
    # SHA-256
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '4. Content Fingerprint'
        '</div>',
        unsafe_allow_html=True
    )


    selected_url = selected_result.get(
        "url",
        ""
    )


    if not selected_url:

        st.error(
            "Selected result does not contain a URL."
        )

        st.stop()


    fingerprint = hashlib.sha256(
        selected_url.encode("utf-8")
    ).hexdigest()


    st.session_state.fingerprint = fingerprint


    st.write(
        "The selected social-media post URL "
        "is converted into a SHA-256 digital fingerprint."
    )


    st.markdown(
        f"""
        <div class="hash-box">
        {fingerprint}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # BLOCKCHAIN
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '5. Stellar Blockchain Verification'
        '</div>',
        unsafe_allow_html=True
    )


    st.write(
        "The selected result is ready to be "
        "recorded on Stellar Testnet."
    )


    # --------------------------------------------------------
    # Build bridge URL
    # --------------------------------------------------------

    bridge_url = (
        "http://localhost:8000/stellar/"
        "?url="
        + quote(
            selected_url,
            safe=""
        )
        + "&hash="
        + fingerprint
        + "&platform="
        + quote(
            selected_result.get(
                "platform",
                ""
            ),
            safe=""
        )
        + "&title="
        + quote(
            selected_result.get(
                "title",
                ""
            ),
            safe=""
        )
    )


    st.link_button(
        "🔐 Open Blockchain Verification",
        bridge_url,
        use_container_width=True
    )


    st.caption(
        "Freighter handles wallet authorization and transaction signing. "
        "Your private key never enters the FaceTrace application."
    )