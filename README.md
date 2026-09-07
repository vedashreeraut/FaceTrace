# FaceTrace

### Discover · Verify · Prove

FaceTrace is a visual evidence discovery and verification platform that helps users discover where a face appears across publicly indexed web and social-media content and create a cryptographically verifiable record of selected evidence.

The system combines computer vision, reverse-image search, explainable evidence scoring, SHA-256 fingerprinting, and Stellar Testnet blockchain verification into one end-to-end workflow.

---

## Overview

FaceTrace transforms an uploaded image into a structured evidence-verification pipeline:

```text
Upload Image
     ↓
Face Detection
     ↓
128-Dimensional Face Encoding
     ↓
Google Lens Reverse Image Search
     ↓
Social-Media Evidence Discovery
     ↓
Evidence Classification & Scoring
     ↓
Canonical Evidence Record
     ↓
SHA-256 Fingerprint
     ↓
Stellar Testnet
     ↓
Blockchain Re-verification
     ↓
✓ Record Verified
```

The goal is not simply to find visually similar content, but to provide a way to document, explain, fingerprint, and later verify the integrity of discovered evidence.

---

## Key Features

### 1. Face Analysis

FaceTrace accepts an image containing a face and performs local face analysis.

The system:

- Detects faces using `face_recognition`
- Validates that a usable face is present
- Generates a 128-dimensional face encoding
- Saves the generated encoding for the current analysis workflow
- Creates an annotated image showing the detected face

This forms the first stage of the FaceTrace pipeline.

---

### 2. Genuine Reverse-Image Search

FaceTrace performs a real reverse-image search using:

- Google Lens
- SerpApi

The uploaded image is sent to the search service and genuine search results are returned.

The application does not use hardcoded example social-media results.

The search process includes both:

- Visual Matches
- Exact Matches

This provides a more useful distinction between direct matches and visually related content.

---

### 3. Social-Media Evidence Discovery

Reverse-image search results are filtered to recognized social-media platforms.

Currently supported platforms include:

- Instagram
- Facebook
- X
- Reddit
- TikTok
- YouTube

The search layer also performs:

- URL normalization
- Duplicate removal
- Dead or unavailable result filtering
- Search-result ranking
- Direct-content detection
- Match-type classification

This helps prioritize useful social-media evidence instead of simply displaying every returned URL.

---

### 4. Evidence Classification

FaceTrace distinguishes between different types of search evidence.

#### Exact Match

The result comes from Google Lens's Exact Matches result set.

An Exact Match provides stronger evidence than a general visual match because the search engine has identified a more direct correspondence.

#### Visual Match

The result is returned by Google Lens as a Visual Match.

A Visual Match indicates that the discovered content is visually similar to the uploaded image, but it should not automatically be interpreted as proof of identity.

#### Related Match

The result is related to the visual search but does not qualify as an exact or direct visual match.

This distinction prevents visually similar search results from being presented as definitive identity evidence.

---

### 5. Evidence Match Score

Each discovered result receives an Evidence Match Score.

The score represents the strength and usefulness of the available search evidence rather than the probability of a person's identity.

The score considers signals such as:

- Google Lens match classification
- Search-result ranking
- Social-media source
- Whether the URL points directly to content
- URL availability
- Associated image data
- Available metadata
- Profile versus direct-content pages

The score is capped between `0` and `100`.

The application also provides an evidence-strength level:

- High
- Moderate
- Low

The Evidence Match Score should be interpreted as an evidence-strength indicator, not as an identity-confidence percentage.

---

### 6. Explainable "Why This Result?"

FaceTrace does not only display a numerical score.

For a selected result, the application explains the evidence contributing to the score.

Examples include:

- Result returned by Google Lens
- Result appears near the top of the search results
- Source is a recognized social platform
- URL points directly to content
- Associated image data is available
- Source metadata is available
- Result is a profile page
- Result is currently reachable

This makes the evidence assessment more transparent and easier to interpret.

---

### 7. Evidence Provenance

After a user selects a social-media result, FaceTrace constructs a canonical evidence record containing key metadata such as:

```json
{
  "platform": "Instagram",
  "title": "Example result",
  "url": "https://www.instagram.com/..."
}
```

The record is deliberately kept small and deterministic.

Only the canonical evidence fields are used to create the cryptographic fingerprint.

---

### 8. SHA-256 Fingerprinting

FaceTrace generates a SHA-256 cryptographic fingerprint from the canonical evidence record.

Conceptually:

```text
Platform + Title + URL
        ↓
Canonical JSON
        ↓
SHA-256
        ↓
64-character hexadecimal fingerprint
```

The canonical JSON representation ensures that the same evidence produces the same fingerprint.

Any change to the canonical evidence data produces a different SHA-256 fingerprint.

For example:

```text
Original Evidence
       ↓
SHA-256
       ↓
Fingerprint A

Modified Evidence
       ↓
SHA-256
       ↓
Fingerprint B

Fingerprint A ≠ Fingerprint B
```

---

### 9. Stellar Blockchain Verification

The generated fingerprint is anchored to the Stellar Testnet.

The workflow is:

```text
Evidence Record
      ↓
SHA-256 Fingerprint
      ↓
Unsigned Stellar Transaction
      ↓
Freighter Wallet
      ↓
User Approval / Signature
      ↓
Stellar Testnet
```

The transaction contains the SHA-256 fingerprint as a Stellar hash memo.

A small native Stellar payment is also included so that the transaction can be submitted and recorded on the Testnet.

FaceTrace then retrieves the confirmed transaction and compares the on-chain fingerprint with the expected fingerprint.

A successful comparison produces:

```text
✓ HASH MATCH
✓ RECORD VERIFIED
```

This provides an independently verifiable integrity record for the selected evidence.

---

### 10. Freighter Wallet Integration

FaceTrace uses Freighter to authorize and sign Stellar Testnet transactions.

The browser prepares the transaction and passes it to Freighter for user approval and signing.

The private wallet key is not handled directly by the FaceTrace browser interface during the signing process.

Freighter is responsible for the user approval and signing step.

---

### 11. Blockchain Re-verification

After the transaction is confirmed, FaceTrace retrieves the transaction from the Stellar Testnet.

The application then:

1. Reads the transaction envelope.
2. Extracts the Stellar hash memo.
3. Converts the memo back into the hexadecimal fingerprint.
4. Compares it with the locally generated SHA-256 fingerprint.
5. Reports whether the hashes match.

Successful verification:

```text
Expected SHA-256
       │
       ▼
On-chain SHA-256
       │
       ▼
      MATCH
       │
       ▼
✓ RECORD VERIFIED
```

A mismatch means that the supplied evidence record does not correspond to the fingerprint stored in the selected blockchain transaction.

---

### 12. Stellar Explorer

Once a blockchain transaction has been confirmed, FaceTrace provides a link to the corresponding Stellar transaction.

The transaction can be independently inspected using a public Stellar Testnet explorer.

This gives the user a way to verify that the fingerprint was actually recorded on the blockchain.

---

### 13. Tamper Demonstration

FaceTrace includes an optional integrity demonstration.

The application can simulate a modification to the local evidence record and recompute its SHA-256 fingerprint.

For example:

```text
Original fingerprint
A83C...72FE

Modified fingerprint
91FA...104C

✗ HASH MISMATCH
```

The demonstration works by modifying the local evidence data, calculating a new fingerprint, and comparing it with the original fingerprint.

The Stellar transaction itself is not modified.

The feature demonstrates why hashing can be used to detect changes to evidence after it has been recorded.

The original local evidence can then be restored in the interface.

---

## System Architecture

```text
                         FaceTrace
                             │
                             ▼
                    ┌─────────────────┐
                    │   Image Upload  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Face Detection  │
                    │   + 128-D      │
                    │    Encoding     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Google Lens   │
                    │    via SerpApi  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Social-Media    │
                    │ Result Filtering│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Evidence        │
                    │ Classification  │
                    │ & Scoring       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Canonical       │
                    │ Evidence Record │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    SHA-256      │
                    │   Fingerprint   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Stellar Testnet │
                    │ + Freighter     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Blockchain      │
                    │ Re-verification │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ HASH MATCH /    │
                    │ HASH MISMATCH   │
                    └─────────────────┘
```

---

## Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Computer Vision

- `face_recognition`
- dlib
- Pillow
- NumPy

### Reverse Image Search

- Google Lens
- SerpApi

### Blockchain

- Stellar Testnet
- Stellar Python SDK
- Freighter Wallet

### Cryptography

- SHA-256

### Configuration

- Python `python-dotenv`

---

## Project Structure

```text
FaceTrace/
│
├── input/
│   └── face.jpg
│
├── output/
│   ├── detected_face.jpg
│   ├── face_encoding.pkl
│   └── search_results.json
│
├── src/
│   ├── server.py
│   ├── features.py
│   ├── web_search.py
│   ├── face_detector.py
│   ├── blockchain.py
│   └── app.py
│
├── stellar/
│   └── index.html
│
├── templates/
│   └── index.html
│
├── .gitignore
├── requirements.txt
├── README.md
└── .env
```

> `src/app.py` and `stellar/index.html` are legacy components retained from earlier development stages. The current application is served through `src/server.py` and `templates/index.html`.

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FaceTrace
```

---

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
SERPAPI_KEY=your_serpapi_api_key
STELLAR_PUBLIC_KEY=your_stellar_testnet_public_key
STELLAR_SECRET_KEY=your_dedicated_testnet_secret_key
```

### Important

Never commit `.env` to GitHub.

The repository `.gitignore` excludes `.env`.

For blockchain testing, use a dedicated Stellar Testnet account rather than a personal or production wallet.

---

## SerpApi Setup

FaceTrace uses SerpApi to access Google Lens search results.

Create a SerpApi account and obtain an API key.

Add the key to:

```env
SERPAPI_KEY=your_serpapi_api_key
```

The application uses Google Lens through SerpApi to perform genuine reverse-image searches.

The project does not rely on hardcoded search results.

---

## Stellar Testnet Setup

FaceTrace uses Stellar Testnet for blockchain verification.

You need:

1. A Stellar Testnet account
2. A funded Testnet account
3. Freighter installed in your browser
4. Freighter configured to use Stellar Testnet

The Testnet account can be funded using Stellar's Testnet Friendbot.

The application's Stellar transaction flow is:

```text
FaceTrace
   ↓
Build transaction
   ↓
Freighter
   ↓
User approves transaction
   ↓
Stellar Testnet
   ↓
Transaction confirmation
   ↓
Fingerprint retrieval
   ↓
Fingerprint comparison
```

---

## Running the Application

From the project root:

```bash
python3 src/server.py
```

The server runs locally at:

```text
http://localhost:8000
```

Open that address in your browser.

---

## Using FaceTrace

### Step 1 — Upload an image

Upload a JPG, JPEG, PNG, or WEBP image containing a clearly visible face.

---

### Step 2 — Analyze the image

Click:

```text
Analyze Image
```

FaceTrace will:

- Detect the face
- Generate the 128-dimensional face encoding
- Perform a Google Lens search
- Retrieve matching and related web results
- Filter social-media results
- Calculate evidence scores

---

### Step 3 — Review social-media evidence

The application displays discovered social-media results.

Results can be filtered by platform.

Each result provides information such as:

- Platform
- Title
- Source URL
- Match type
- Evidence Match Score
- Evidence strength

---

### Step 4 — Select a result

Select a result to view its Evidence Intelligence panel.

The panel shows:

- Match classification
- Evidence Match Score
- Evidence-strength level
- Supporting reasons
- Source information
- Relevant evidence metadata

---

### Step 5 — Verify on Stellar

Click:

```text
Verify on Stellar
```

FaceTrace prepares the evidence fingerprint and Stellar Testnet transaction.

Freighter will open for the signing step.

Approve the transaction through Freighter.

---

### Step 6 — Wait for confirmation

After the transaction is submitted, FaceTrace retrieves the confirmed transaction from Stellar Testnet.

The blockchain fingerprint is compared with the fingerprint generated from the selected evidence.

A successful verification displays:

```text
✓ HASH MATCH — RECORD VERIFIED
```

---

### Step 7 — View the blockchain transaction

The application provides a link to the corresponding Stellar Testnet transaction.

Open the transaction in the Stellar explorer to independently inspect the blockchain record.

---

### Step 8 — Test integrity

After successful verification, the optional:

```text
Simulate Tampering
```

feature can be used to demonstrate how modifying the evidence changes its fingerprint.

The application should then display:

```text
✗ HASH MISMATCH
```

Use the restore control to return the evidence display to its original state.

---

## Verification Flow

```text
Evidence Record
      ↓
SHA-256 Fingerprint
      ↓
Stellar Testnet Transaction
      ↓
Freighter Signature
      ↓
Transaction Confirmation
      ↓
Retrieve On-Chain Fingerprint
      ↓
Compare Hashes
      ↓
┌───────────────────────┐
│ Hashes Match?         │
└───────────┬───────────┘
            │
       ┌────┴────┐
       │         │
      YES        NO
       │         │
       ▼         ▼
  ✓ VERIFIED   ✗ MISMATCH
```

---

## Evidence Data Model

The canonical evidence record used for fingerprinting contains:

```json
{
  "platform": "Instagram",
  "title": "Example result",
  "url": "https://www.instagram.com/example"
}
```

The record is converted into a deterministic canonical representation before hashing.

Conceptually:

```text
Evidence
   ↓
Canonical Representation
   ↓
SHA-256
   ↓
Fingerprint
```

This ensures that verification is based on a reproducible representation of the evidence.

---

## Blockchain Data Model

The SHA-256 fingerprint is stored on Stellar Testnet as a hash memo.

```text
SHA-256 fingerprint
        ↓
Stellar Hash Memo
        ↓
Stellar Testnet Transaction
```

The fingerprint is not stored as ordinary human-readable text in the memo.

The application uses Stellar's hash-memo functionality so that the 32-byte SHA-256 digest can be represented directly.

---

## Security and Integrity Model

FaceTrace separates three concepts:

### Discovery

Google Lens and SerpApi are used to discover publicly indexed content that may be related to the uploaded image.

### Evidence Assessment

The application classifies and scores results using available search and source signals.

### Integrity Verification

The selected evidence record is fingerprinted with SHA-256 and the fingerprint is anchored to Stellar Testnet.

These layers should not be confused.

A successful blockchain verification proves that the retrieved evidence record matches the fingerprint that was previously recorded on-chain.

It does not prove that the original online content was truthful, that a person is definitely the person shown in the image, or that the content itself is authentic.

---

## Privacy Considerations

FaceTrace processes the uploaded image as part of the analysis workflow.

The current hackathon implementation focuses on functionality, evidence discovery, and integrity verification rather than providing a complete privacy-preserving identity system.

Search providers may receive the uploaded image as part of the reverse-image search process.

Users should therefore avoid uploading sensitive or private images that they are not comfortable sending to a third-party image-search provider.

---

## Known Limitations

### 1. Search Engine Dependency

FaceTrace relies on Google Lens through SerpApi.

Search results depend on what the external search service can currently discover and index.

Results may change over time.

---

### 2. Search Result Accuracy

A visual match is not proof of identity.

Reverse-image search engines can return:

- Similar people
- Similar scenes
- Reposts
- Related articles
- Profiles
- Memes
- Cropped or edited versions
- Other visually related content

The Evidence Match Score should therefore be treated as evidence strength rather than an identity probability.

---

### 3. Social-Media Availability

Some social-media URLs may become unavailable because:

- A post was deleted
- An account became private
- A platform changed the URL
- Access is restricted
- The content was removed

FaceTrace attempts to filter obvious unavailable results, but external websites remain outside the application's control.

---

### 4. Public Search Restrictions

The application works with publicly indexed search results.

It does not attempt to bypass:

- Login requirements
- CAPTCHA challenges
- Platform security controls
- Access restrictions
- Private accounts

---

### 5. Stellar Testnet

The blockchain implementation uses Stellar Testnet.

Testnet transactions are intended for experimentation and demonstration and do not represent production-value financial transactions.

---

### 6. Local Application

The current project is designed primarily as a local demonstration application.

The backend runs through Flask on:

```text
http://localhost:8000
```

Production deployment, authentication, database persistence, and multi-user infrastructure are outside the scope of the current implementation.

---

### 7. Evidence Persistence

The current implementation focuses on the evidence-verification workflow.

It does not provide a full production database-backed evidence management system.

The blockchain fingerprint acts as an integrity anchor rather than a complete storage system for the original evidence.

---

## Design Philosophy

FaceTrace is built around three principles:

### Discover

Use real visual search to locate publicly indexed content.

### Explain

Show how a result was classified and why it received its Evidence Match Score.

### Prove

Create a cryptographic fingerprint and anchor it to a blockchain so that the selected evidence record can later be checked for tampering.

This creates a pipeline from visual discovery to verifiable evidence integrity.

---

## Why Blockchain?

A local SHA-256 hash can detect whether data has changed when the original reference value is trusted.

Blockchain adds a public, independently inspectable record of that fingerprint.

In FaceTrace:

```text
Evidence
   ↓
SHA-256
   ↓
Stellar Testnet
   ↓
Publicly inspectable transaction
```

The blockchain does not determine whether the evidence is true.

Instead, it provides an integrity anchor for the evidence representation that FaceTrace recorded.

---

## Example Evidence Flow

Suppose a user uploads an image and the search engine returns a social-media post.

FaceTrace may create:

```json
{
  "platform": "Reddit",
  "title": "Example discussion",
  "url": "https://www.reddit.com/r/example/..."
}
```

The record is fingerprinted:

```text
Canonical Evidence
       ↓
SHA-256
       ↓
a83c9b...72fe
```

The fingerprint is then recorded on Stellar Testnet.

Later, the same evidence record can be processed again:

```text
Current Evidence
       ↓
SHA-256
       ↓
a83c9b...72fe
       ↓
Compare with blockchain
       ↓
✓ MATCH
```

If the record has been modified:

```text
Modified Evidence
       ↓
SHA-256
       ↓
91fa21...104c
       ↓
Compare with blockchain
       ↓
✗ MISMATCH
```

---

## Development

The application can be run directly from the project root.

Start the server:

```bash
python3 src/server.py
```

Then open:

```text
http://localhost:8000
```

The main application frontend is located at:

```text
templates/index.html
```

The Flask backend is located at:

```text
src/server.py
```

Core functionality is organized into:

```text
src/face_detector.py
src/web_search.py
src/features.py
src/server.py
```

---

## Main Components

### `src/face_detector.py`

Handles:

- Image loading
- Face detection
- Face encoding generation
- Annotated output generation

---

### `src/web_search.py`

Handles:

- SerpApi configuration
- Google Lens image upload
- Visual Matches search
- Exact Matches search
- Social-platform filtering
- URL normalization
- Deduplication
- Availability checks
- Search-result ranking

---

### `src/features.py`

Handles:

- Canonical evidence records
- SHA-256 fingerprint generation
- Match classification
- Social-platform detection
- Evidence scoring
- Evidence explanation data

---

### `src/server.py`

Handles:

- Flask web application
- Image upload
- Face analysis workflow
- Search workflow
- Evidence selection
- Stellar transaction preparation
- Blockchain verification
- Tamper demonstration API
- Frontend API endpoints

---

### `templates/index.html`

Contains the main FaceTrace user interface, including:

- Image upload
- Face analysis
- Search results
- Evidence intelligence
- Blockchain verification
- Freighter integration
- Tamper demonstration

---

## API Endpoints

The Flask application exposes the following primary endpoints.

### Analyze

```text
POST /api/analyze
```

Analyzes the uploaded image and returns face-analysis and search results.

---

### Prepare Transaction

```text
POST /api/prepare-transaction
```

Creates the Stellar Testnet transaction containing the SHA-256 evidence fingerprint.

---

### Verify Transaction

```text
POST /api/verify-transaction
```

Retrieves the Stellar transaction and verifies the blockchain fingerprint against the expected evidence fingerprint.

---

### Tamper Check

```text
POST /api/tamper-check
```

Creates a local modified representation of the evidence and demonstrates the resulting hash mismatch.

---

## Requirements

A typical environment requires:

- Python 3
- Flask
- face-recognition
- dlib
- Pillow
- NumPy
- SerpApi
- python-dotenv
- Stellar SDK

A supported browser is also required for Freighter wallet integration.

---

## Git and Configuration

Before committing the project:

Make sure `.env` is ignored:

```gitignore
venv/
.env
__pycache__/
*.pyc
.DS_Store
```

Do not commit API keys or wallet secrets.

---

## Demo

The recommended end-to-end demonstration is:

```text
1. Open FaceTrace
2. Upload a face image
3. Run analysis
4. Show face detection
5. Show Google Lens results
6. Show social-media evidence
7. Select a result
8. Show Evidence Match Score
9. Show "Why This Result?"
10. Generate SHA-256 fingerprint
11. Click Verify on Stellar
12. Approve the transaction in Freighter
13. Show transaction confirmation
14. Show HASH MATCH — RECORD VERIFIED
15. Open the Stellar transaction
16. Demonstrate tampering
17. Show HASH MISMATCH
18. Restore the evidence
```

The complete pipeline demonstrates:

```text
Face Scan
    ↓
Social Post Found
    ↓
Evidence Assessed
    ↓
Fingerprint Created
    ↓
Blockchain Upload
    ↓
Blockchain Verification
```

---

## Future Improvements

Potential future improvements include:

- Persistent database-backed evidence history
- User authentication
- Multiple evidence records per investigation
- Evidence export and reporting
- Stronger duplicate detection
- Additional reverse-image search providers
- More social-media sources
- Advanced face-comparison workflows
- Privacy-preserving image processing
- Production blockchain infrastructure
- Cloud deployment
- Automated evidence monitoring
- Audit logs
- Multi-user investigation workspaces

These features are outside the scope of the current hackathon implementation.

---

## Disclaimer

FaceTrace is an experimental evidence-discovery and integrity-verification system.

A search result, visual match, Evidence Match Score, or blockchain verification must not be interpreted as definitive proof of a person's identity or as proof that online content is factually authentic.

The blockchain verifies the integrity of the recorded evidence representation, not the truthfulness of the underlying content.

Users are responsible for ensuring that their use of the system complies with applicable laws, platform policies, privacy requirements, and consent requirements.

---

## License

This project was developed as a hackathon/academic project.

Add the appropriate license here before distributing the project publicly.

Example:

```text
MIT License
```

---

## Acknowledgements

FaceTrace uses the following technologies and services:

- `face_recognition`
- dlib
- Google Lens
- SerpApi
- Flask
- Stellar
- Stellar Python SDK
- Freighter Wallet

---

## Project Status

**Status:** Hackathon Prototype

The current version demonstrates a complete local end-to-end workflow:

```text
Image
  ↓
Face Detection
  ↓
Reverse Image Search
  ↓
Social Evidence
  ↓
Evidence Intelligence
  ↓
SHA-256 Fingerprint
  ↓
Stellar Testnet
  ↓
Blockchain Re-verification
```

---

## Repository

GitHub Repository:

```text
<YOUR_GITHUB_REPOSITORY_URL>
```

---

## Demo Video

Demo Video:

```text
<YOUR_DEMO_VIDEO_URL>
```

---

## Built With

```text
Python
Flask
face_recognition
Google Lens
SerpApi
SHA-256
Stellar Testnet
Freighter
HTML
CSS
JavaScript
```

---

# FaceTrace

### Discover · Verify · Prove