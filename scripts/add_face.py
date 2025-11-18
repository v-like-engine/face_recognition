#!/usr/bin/env python3
"""
Utility script to add a known face to the database
Usage: python scripts/add_face.py <image_path> <name>
"""
import sys
import requests
from pathlib import Path


def add_face(image_path: str, name: str, api_url: str = "http://localhost:8000/api/v1"):
    """Add a face to the database"""

    # Check if file exists
    if not Path(image_path).exists():
        print(f"❌ Error: File not found: {image_path}")
        return False

    try:
        print(f"📤 Uploading {image_path}...")

        with open(image_path, "rb") as f:
            response = requests.post(
                f"{api_url}/faces/add",
                files={"file": f},
                data={"name": name}
            )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Success: {result.get('message')}")
                return True
            else:
                print(f"❌ Error: {result.get('message')}")
                return False
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
    if len(sys.argv) < 3:
        print("Usage: python scripts/add_face.py <image_path> <name>")
        print("")
        print("Example:")
        print("  python scripts/add_face.py photos/john.jpg \"John Doe\"")
        sys.exit(1)

    image_path = sys.argv[1]
    name = sys.argv[2]

    print("=" * 60)
    print("  Add Face to Database")
    print("=" * 60)
    print(f"Image: {image_path}")
    print(f"Name:  {name}")
    print("")

    success = add_face(image_path, name)

    if success:
        print("")
        print("✨ Face added successfully!")
    else:
        print("")
        print("Failed to add face. Please check the error message above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
