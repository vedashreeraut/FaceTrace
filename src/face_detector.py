import cv2
import face_recognition
import numpy as np
import os
import pickle


INPUT_IMAGE = "input/face.jpg"
OUTPUT_IMAGE = "output/detected_face.jpg"
OUTPUT_ENCODING = "output/face_encoding.pkl"


def detect_and_encode_face():

    # Check input image
    if not os.path.exists(INPUT_IMAGE):
        print("ERROR: input/face.jpg not found.")
        return

    # Load image
    image = face_recognition.load_image_file(INPUT_IMAGE)

    # Detect faces
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) == 0:
        print("ERROR: No face detected.")
        return

    if len(face_locations) > 1:
        print(f"ERROR: {len(face_locations)} faces detected.")
        print("Please use an image containing only one face.")
        return

    print("✓ Face detected")

    # Generate face encoding
    encodings = face_recognition.face_encodings(
        image,
        face_locations
    )

    if not encodings:
        print("ERROR: Could not generate face encoding.")
        return

    face_encoding = encodings[0]

    print("✓ Face encoding generated")
    print(f"✓ Encoding dimensions: {len(face_encoding)}")

    # Save encoding
    with open(OUTPUT_ENCODING, "wb") as file:
        pickle.dump(face_encoding, file)

    print(f"✓ Encoding saved to {OUTPUT_ENCODING}")

    # Convert RGB → BGR for OpenCV
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Draw face rectangle
    top, right, bottom, left = face_locations[0]

    cv2.rectangle(
        image_bgr,
        (left, top),
        (right, bottom),
        (0, 255, 0),
        2
    )

    cv2.putText(
        image_bgr,
        "Face Detected",
        (left, top - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # Save annotated image
    cv2.imwrite(OUTPUT_IMAGE, image_bgr)

    print(f"✓ Annotated image saved to {OUTPUT_IMAGE}")
    print("\nSPRINT 1 COMPLETE ✓")


if __name__ == "__main__":
    detect_and_encode_face()