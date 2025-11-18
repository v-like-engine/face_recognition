#!/usr/bin/env python3
"""
Utility script to recognize faces in an image
Usage: python scripts/recognize.py <image_path> [tolerance]
"""
import sys
import requests
from pathlib import Path


def recognize_faces(image_path: str, tolerance: float = None, api_url: str = "http://localhost:8000/api/v1"):
    """Recognize faces in an image"""

    # Check if file exists
    if not Path(image_path).exists():
        print(f"❌ Error: File not found: {image_path}")
        return False

    try:
        print(f"📤 Analyzing {image_path}...")
        print("")

        with open(image_path, "rb") as f:
            data = {}
            if tolerance is not None:
                data["tolerance"] = tolerance

            response = requests.post(
                f"{api_url}/recognize",
                files={"file": f},
                data=data
            )

        if response.status_code == 200:
            result = response.json()

            print("=" * 60)
            print("  Recognition Results")
            print("=" * 60)
            print("")
            print(f"Faces detected: {result.get('faces_found', 0)}")
            print("")

            if result.get('faces'):
                for i, face in enumerate(result['faces'], 1):
                    name = face.get('name', 'Unknown')
                    confidence = face.get('confidence', 0)
                    location = face.get('location', {})

                    print(f"Face #{i}:")
                    print(f"  Name:       {name}")
                    print(f"  Confidence: {confidence:.2%}")
                    print(f"  Location:   top={location.get('top')}, right={location.get('right')}, "
                          f"bottom={location.get('bottom')}, left={location.get('left')}")
                    print("")
            else:
                print("No faces detected in the image.")
                print("")

            print("=" * 60)
            return True

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Is the server running?")
        print("   Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/recognize.py <image_path> [tolerance]")
        print("")
        print("Example:")
        print("  python scripts/recognize.py photos/group.jpg")
        print("  python scripts/recognize.py photos/group.jpg 0.5")
        print("")
        print("Tolerance: 0.4-0.5 = strict, 0.6 = balanced, 0.7-0.8 = lenient")
        sys.exit(1)

    image_path = sys.argv[1]
    tolerance = float(sys.argv[2]) if len(sys.argv) > 2 else None

    success = recognize_faces(image_path, tolerance)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
