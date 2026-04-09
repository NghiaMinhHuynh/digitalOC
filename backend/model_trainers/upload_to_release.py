"""
The purpose of this file is to upload a .joblib model to GitHub Releases after it was re-trained
Each model gets its own separate tag
"""

import io
import os
import joblib
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "nworobec/digitalOC"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def upload_model_to_release(model, filename: str, tag: str):
    """Upload a model directly to its own dedicated GitHub Release."""

    # Find any existing release (including drafts) with this tag
    r = requests.get(f"https://api.github.com/repos/{REPO}/releases", headers=HEADERS)
    r.raise_for_status()
    existing = next((rel for rel in r.json() if rel["tag_name"] == tag), None)

    if existing:
        release_id = existing["id"]
        upload_url = existing["upload_url"].replace("{?name,label}", "")
        # Remove existing assets so we can re-upload
        for asset in existing.get("assets", []):
            requests.delete(f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}", headers=HEADERS)
        # Publish if it's currently a draft
        if existing.get("draft"):
            requests.patch(
                f"https://api.github.com/repos/{REPO}/releases/{release_id}",
                headers=HEADERS,
                json={"draft": False}
            ).raise_for_status()
    else:
        # No existing release — clean up any stale tag and create fresh
        requests.delete(f"https://api.github.com/repos/{REPO}/git/refs/tags/{tag}", headers=HEADERS)
        r = requests.post(
            f"https://api.github.com/repos/{REPO}/releases",
            headers=HEADERS,
            json={"tag_name": tag, "name": tag, "body": "Auto-updated", "draft": False}
        )
        r.raise_for_status()
        upload_url = r.json()["upload_url"].replace("{?name,label}", "")

    # Serialize and upload
    buffer = io.BytesIO()
    joblib.dump(model, buffer)
    buffer.seek(0)
    requests.post(
        f"{upload_url}?name={filename}",
        headers={**HEADERS, "Content-Type": "application/octet-stream"},
        data=buffer.read()
    ).raise_for_status()
    print(f"Uploaded {filename} to GitHub Releases with tag: '{tag}'")