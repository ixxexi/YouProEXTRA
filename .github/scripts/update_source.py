"""Rewrite source/ytplus.json from this repo's published YouTubePlus releases."""
import json
import os
import re
import subprocess

REPO = os.environ.get("GITHUB_REPOSITORY", "ixxexi/YouProEXTRA")
RAW = f"https://raw.githubusercontent.com/{REPO}/main/source"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "source", "ytplus.json")
ASSET = re.compile(r"^YouTubePlus_(?P<yt>[\d.]+)_(?P<ytl>.+)\.ipa$")


def releases():
    out = subprocess.run(
        ["gh", "api", "--paginate", "--jq", ".[]", f"repos/{REPO}/releases?per_page=100"],
        check=True, capture_output=True, text=True,
    ).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


versions = []
for rel in releases():
    if rel["draft"] or not rel["tag_name"].startswith("ytl-ipa"):
        continue
    for asset in rel["assets"]:
        m = ASSET.match(asset["name"])
        if not m:
            continue
        versions.append({
            "version": m["yt"],
            "date": rel["published_at"][:10],
            "localizedDescription": f"YouTube {m['yt']} | YouTubePlus {m['ytl']} (plain build)",
            "downloadURL": asset["browser_download_url"],
            "size": asset["size"],
            "minOSVersion": "17.0",
            "_published": rel["published_at"],
        })
        break

versions.sort(key=lambda v: v.pop("_published"), reverse=True)

apps = []
if versions:
    latest = versions[0]
    apps.append({
        "name": "YouTubePlus",
        "bundleIdentifier": "com.google.ios.youtube",
        "developerName": "dayanch96",
        "subtitle": "Plain YTLite build",
        "localizedDescription": "YouTubePlus (YTLite) with no extra tweaks. Built from this fork.",
        "iconURL": f"{RAW}/icon.png",
        "tintColor": "FF0000",
        "category": "photo-video",
        "version": latest["version"],
        "versionDate": latest["date"],
        "versionDescription": latest["localizedDescription"],
        "downloadURL": latest["downloadURL"],
        "size": latest["size"],
        "versions": versions,
    })

source = {
    "name": "My YouTubePlus",
    "identifier": f"com.{REPO.split('/')[0].lower()}.ytplus",
    "apiVersion": "v2",
    "subtitle": "Personal plain YouTubePlus builds",
    "iconURL": f"{RAW}/icon.png",
    "sourceURL": f"{RAW}/ytplus.json",
    "apps": apps,
    "news": [],
}

with open(OUT, "w") as f:
    json.dump(source, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"{len(versions)} version(s) written")
