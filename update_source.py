import zipfile, plistlib, json, os
from datetime import date

REPO = os.environ["GITHUB_REPOSITORY"]
BASE = f"https://github.com/{REPO}/raw/main/ipa"

def parse_ipa(p):
    with zipfile.ZipFile(p) as z:
        n = next(x for x in z.namelist()
                 if x.startswith("Payload/") and x.endswith(".app/Info.plist")
                 and x.count("/") == 2)
        info = plistlib.loads(z.read(n))
    return {
        "name": info.get("CFBundleDisplayName") or info.get("CFBundleName"),
        "bundleIdentifier": info["CFBundleIdentifier"],
        "version": info["CFBundleShortVersionString"],
        "minOSVersion": info.get("MinimumOSVersion", "13.0"),
    }

with open("source.json", encoding="utf-8") as f:
    src = json.load(f)

for fn in os.listdir("ipa"):
    if not fn.endswith(".ipa"):
        continue
    m = parse_ipa(os.path.join("ipa", fn))
    match_name = fn.split("__")[0] if "__" in fn else None
    key = match_name or m["name"]

    ver = {
        "version": m["version"],
        "date": date.today().isoformat(),
        "downloadURL": f"{BASE}/{fn}",
        "size": os.path.getsize(os.path.join("ipa", fn)),
        "minOSVersion": m["minOSVersion"],
    }

    app = next((a for a in src["apps"]
                if a["name"] == key or a["bundleIdentifier"] == m["bundleIdentifier"]), None)
    if app:
        app["versions"] = [v for v in app["versions"] if v["version"] != m["version"]]
        app["versions"].insert(0, ver)
    else:
        src["apps"].append({
            "name": m["name"],
            "bundleIdentifier": m["bundleIdentifier"],
            "developerName": "You",
            "versions": [ver],
        })

with open("source.json", "w", encoding="utf-8") as f:
    json.dump(src, f, indent=2, ensure_ascii=False)
print("done")
