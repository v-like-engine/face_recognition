#!/usr/bin/env python3
"""
Utility script to list all known faces in the database
Usage: python scripts/list_faces.py
"""
import requests


def list_faces(api_url: str = "http://localhost:8000/api/v1"):
    """List all known faces"""

    try:
        response = requests.get(f"{api_url}/faces")

        if response.status_code == 200:
            result = response.json()

            print("=" * 60)
            print("  Known Faces Database")
            print("=" * 60)
            print("")
            print(f"Total encodings: {result.get('total_encodings', 0)}")
            print(f"Unique people:   {result.get('unique_people', 0)}")
            print("")

            if result.get('people'):
                print("People in database:")
                print("")
                for person in sorted(result.get('people', [])):
                    count = result.get('counts', {}).get(person, 0)
                    print(f"  • {person} ({count} encoding{'s' if count != 1 else ''})")
            else:
                print("No faces in database yet.")
                print("")
                print("Add a face with:")
                print("  python scripts/add_face.py <image_path> <name>")

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
    list_faces()


if __name__ == "__main__":
    main()
