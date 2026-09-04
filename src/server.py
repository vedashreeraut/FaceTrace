import os
import json
import hashlib
import tempfile
from features import (
    build_evidence_record,
    fingerprint_record
)

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)
from dotenv import load_dotenv

import face_recognition
from PIL import Image

from web_search import search_image

from stellar_sdk import (
    Network,
    Server,
    TransactionBuilder,
    Keypair,
    Asset,
    Operation
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

STELLAR_PUBLIC_KEY = os.getenv(
    "STELLAR_PUBLIC_KEY"
)

HORIZON_URL = (
    "https://horizon-testnet.stellar.org"
)

SEARCH_RESULTS_FILE = (
    "output/search_results.json"
)


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder="../templates"
)


# ============================================================
# STELLAR SERVER
# ============================================================

stellar_server = Server(
    HORIZON_URL
)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# ANALYZE IMAGE
# ============================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    temp_path = None

    try:

        # ----------------------------------------------------
        # Check upload
        # ----------------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "No image uploaded."
            }), 400


        uploaded_file = request.files[
            "image"
        ]


        if uploaded_file.filename == "":

            return jsonify({
                "success": False,
                "error": "No image selected."
            }), 400


        # ----------------------------------------------------
        # Save temporary image
        # ----------------------------------------------------

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        temp_path = temp_file.name

        temp_file.close()


        image = Image.open(
            uploaded_file
        ).convert("RGB")


        # Keep image reasonably sized
        image.thumbnail(
            (1600, 1600)
        )


        # SerpApi image limit is 500 KB;
        # target well below that.
        quality = 90

        while quality >= 40:

            image.save(
                temp_path,
                format="JPEG",
                quality=quality,
                optimize=True
            )

            if (
                os.path.getsize(
                    temp_path
                ) <= 450_000
            ):
                break

            quality -= 5


        # ----------------------------------------------------
        # FACE DETECTION
        # ----------------------------------------------------

        cv_image = (
            face_recognition
            .load_image_file(
                temp_path
            )
        )


        face_locations = (
            face_recognition
            .face_locations(
                cv_image
            )
        )


        if len(face_locations) == 0:

            return jsonify({
                "success": False,
                "error": "No face detected."
            }), 400


        if len(face_locations) > 1:

            return jsonify({
                "success": False,
                "error": (
                    f"{len(face_locations)} faces "
                    "detected. Please use an image "
                    "containing one face."
                )
            }), 400


        encodings = (
            face_recognition
            .face_encodings(
                cv_image,
                face_locations
            )
        )


        if not encodings:

            return jsonify({
                "success": False,
                "error": (
                    "Face detected, but encoding "
                    "could not be generated."
                )
            }), 400


        # ----------------------------------------------------
        # GENUINE WEB SEARCH
        # ----------------------------------------------------

        results = search_image(
            temp_path
        )
        # ----------------------------------------------------
# Build evidence records
# ----------------------------------------------------

        evidence_results = []

        for result in results:

            evidence_results.append(
            build_evidence_record(
                result
            )
        )


        # ----------------------------------------------------
        # Return results
        # ----------------------------------------------------

        return jsonify({
            "success": True,

            "face": {
                "detected": True,
                "encoding_dimensions": len(
                    encodings[0]
                )
            },

            "results": evidence_results
        })


    except Exception as error:

        print(
            f"Analyze error: {error}"
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.unlink(temp_path)


# ============================================================
# PREPARE STELLAR TRANSACTION
# ============================================================

@app.route(
    "/api/prepare-transaction",
    methods=["POST"]
)
def prepare_transaction():

    try:

        if not STELLAR_PUBLIC_KEY:

            return jsonify({
                "success": False,
                "error": (
                    "STELLAR_PUBLIC_KEY is missing "
                    "from .env."
                )
            }), 500


        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "error": "No transaction data provided."
            }), 400


        social_result = data.get(
            "result"
        )


        if not social_result:

            return jsonify({
                "success": False,
                "error": "No social-media result selected."
            }), 400


        # ----------------------------------------------------
# Generate fingerprint from canonical evidence record
# ----------------------------------------------------

        evidence_record = build_evidence_record(
            social_result
        )

        fingerprint = evidence_record[
             "sha256"
        ]


        # ----------------------------------------------------
        # Load Stellar account
        # ----------------------------------------------------

        account = (
            stellar_server
            .load_account(
                STELLAR_PUBLIC_KEY
            )
        )


        # ----------------------------------------------------
        # Build unsigned transaction
        # ----------------------------------------------------

        transaction = (
            TransactionBuilder(
                source_account=account,

                network_passphrase="Test SDF Network ; September 2015",

                base_fee=100
            )

            .add_hash_memo(
                fingerprint
            )

            .append_payment_op(
                destination=(
                    STELLAR_PUBLIC_KEY
                ),

                amount="0.0000001",

                asset=Asset.native()
            )

            .set_timeout(30)

            .build()
        )


        return jsonify({
            "success": True,

            "fingerprint": fingerprint,
            
            "evidence": evidence_record,

            "xdr": transaction.to_xdr(),

            "wallet": STELLAR_PUBLIC_KEY,

            "network": "Stellar Testnet"
        })


    except Exception as error:

        print(
            f"Prepare transaction error: {error}"
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# SUBMIT SIGNED STELLAR TRANSACTION
# ============================================================

@app.route(
    "/api/submit-transaction",
    methods=["POST"]
)
def submit_transaction():

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "error": "No transaction supplied."
            }), 400


        signed_xdr = data.get(
            "signed_xdr"
        )


        if not signed_xdr:

            return jsonify({
                "success": False,
                "error": "Signed transaction is missing."
            }), 400


        # ----------------------------------------------------
        # Reconstruct signed transaction
        # ----------------------------------------------------

        transaction = (
            TransactionBuilder
            .from_xdr(
                signed_xdr,
                Network
                .TESTNET_NETWORK_PASSPHRASE
            )
        )


        # ----------------------------------------------------
        # Submit
        # ----------------------------------------------------

        response = (
            stellar_server
            .submit_transaction(
                transaction
            )
        )


        transaction_hash = response[
            "hash"
        ]


        return jsonify({
            "success": True,
            "transaction_hash": transaction_hash
        })


    except Exception as error:

        print(
            f"Submit transaction error: {error}"
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# VERIFY TRANSACTION
# ============================================================

@app.route(
    "/api/verify-transaction",
    methods=["POST"]
)
def verify_transaction():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No verification data supplied."
            }), 400

        transaction_hash = data.get("transaction_hash")
        original_fingerprint = data.get("fingerprint")

        if not transaction_hash:
            return jsonify({
                "success": False,
                "error": "Transaction hash is missing."
            }), 400

        if not original_fingerprint:
            return jsonify({
                "success": False,
                "error": "Fingerprint is missing."
            }), 400

        # --------------------------------------------------
        # Retrieve the confirmed transaction
        # --------------------------------------------------

        transaction_data = (
            stellar_server
            .transactions()
            .transaction(transaction_hash)
            .call()
        )

        if not transaction_data.get("successful", False):
            return jsonify({
                "success": False,
                "error": "Transaction was not successful."
            }), 400

        # --------------------------------------------------
        # Parse the transaction envelope
        # --------------------------------------------------

        envelope_xdr = transaction_data["envelope_xdr"]

        envelope = (
            TransactionBuilder
            .from_xdr(
                envelope_xdr,
                Network.TESTNET_NETWORK_PASSPHRASE
            )
        )

        # --------------------------------------------------
        # The memo is on the underlying transaction
        # --------------------------------------------------

        memo = envelope.transaction.memo

        if memo is None:
            return jsonify({
                "success": False,
                "error": "No memo found in transaction."
            }), 400

        # --------------------------------------------------
        # HashMemo in stellar-sdk 16 uses memo_hash
        # --------------------------------------------------

        if not hasattr(memo, "memo_hash"):
            return jsonify({
                "success": False,
                "error": (
                    "Transaction does not contain "
                    "a SHA-256 hash memo."
                )
            }), 400

        blockchain_fingerprint = (
            bytes(memo.memo_hash).hex()
        )

        # --------------------------------------------------
        # Compare
        # --------------------------------------------------

        verified = (
            blockchain_fingerprint.lower()
            == original_fingerprint.lower()
        )

        print()
        print("=" * 60)
        print("BLOCKCHAIN VERIFICATION")
        print("=" * 60)
        print(
            f"Original fingerprint : {original_fingerprint}"
        )
        print(
            f"Blockchain fingerprint: {blockchain_fingerprint}"
        )
        print(
            f"Verification result   : {verified}"
        )
        print("=" * 60)

        return jsonify({
            "success": True,
            "verified": verified,
            "transaction_hash": transaction_hash,
            "original_fingerprint": original_fingerprint,
            "blockchain_fingerprint": blockchain_fingerprint
        })

    except Exception as error:

        print(
            f"Verification error: {error}"
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
        
# ============================================================
# TAMPER DEMONSTRATION
# ============================================================

@app.route(
    "/api/tamper-check",
    methods=["POST"]
)
def tamper_check():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No evidence record supplied."
            }), 400


        evidence = data.get(
            "evidence"
        )

        if not evidence:
            return jsonify({
                "success": False,
                "error": "Evidence record is missing."
            }), 400


        # ----------------------------------------------------
        # Original fingerprint
        # ----------------------------------------------------

        original_fingerprint = (
            fingerprint_record(
                evidence
            )
        )


        # ----------------------------------------------------
        # Simulate a modification
        #
        # We deliberately alter the title.
        # ----------------------------------------------------

        tampered_evidence = dict(
            evidence
        )


        original_title = str(
            tampered_evidence.get(
                "title",
                ""
            )
        )


        tampered_evidence[
            "title"
        ] = (
            original_title +
            " [MODIFIED]"
        )


        # ----------------------------------------------------
        # New fingerprint
        # ----------------------------------------------------

        tampered_fingerprint = (
            fingerprint_record(
                tampered_evidence
            )
        )


        # ----------------------------------------------------
        # Compare
        # ----------------------------------------------------

        detected = (
            original_fingerprint
            !=
            tampered_fingerprint
        )


        return jsonify({

            "success": True,

            "tampering_detected":
                detected,

            "original_fingerprint":
                original_fingerprint,

            "tampered_fingerprint":
                tampered_fingerprint,

            "original_title":
                original_title,

            "tampered_title":
                tampered_evidence["title"]

        })


    except Exception as error:

        print(
            f"Tamper check error: {error}"
        )

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 500
# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("                FACETRACE")
    print("=" * 60)
    print()
    print(
        "Starting single-page application..."
    )
    print()
    print(
        "Open: http://localhost:8000"
    )
    print()
    print("=" * 60)


    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False
    )