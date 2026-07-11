import json, os
from datetime import datetime

REPO = os.environ["GITHUB_REPOSITORY"]
BASE = f"https://github.com/{REPO}/raw/main/ipa"
APPS_DIR = "apps"
STATE = "versions.json"

def bump(v):
    major, minor = v.split(".")
    minor = int(minor) + 1
    if minor > 9:
        return f"{int(major)+1}.0"
    return f"{major}.{minor}"

# 读取记账文件(记录每个软件名的当前版本和历史)
if os.path.exists(STATE):
    with open(STATE, encoding="utf-8") as f:
        state = json.load(f)
else:
    state = {}

os.makedirs(APPS_DIR, exist_ok=True)
os.makedirs("ipa", exist_ok=True)

# 扫描 ipa 文件夹,找出还没登记过的新文件
known = set()
for name, data in state.items():
    for v in data["versions"]:
        known.add(v["file"])

files = sorted(os.listdir("ipa"))
for fn in files:
    if not fn.endswith(".ipa") or fn in known:
        continue
    # 文件名格式:软件名__原文件名.ipa
    if "__" in fn:
        app_name = fn.split("__")[0]
    else:
        app_name = os.path.splitext(fn)[0]

    if app_name not in state:
        state[app_name] = {"current": "1.0", "versions": []}
        ver = "1.0"
    else:
        ver = bump(state[app_name]["current"])
        state[app_name]["current"] = ver

    entry = {
        "version": ver,
        "file": fn,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "size": os.path.getsize(os.path.join("ipa", fn)),
        "downloadURL": f"{BASE}/{fn}",
    }
    state[app_name]["versions"].insert(0, entry)  # 最新的排最前

# 保存记账文件
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

# 生成总订阅 source.json
apps = []
for name, data in state.items():
    apps.append({
        "name": name,
        "bundleIdentifier": f"com.dogt.{abs(hash(name)) % 100000}",
        "developerName": "dogt",
        "versions": [
            {
                "version": v["version"],
                "date": v["date"],
                "downloadURL": v["downloadURL"],
                "size": v["size"],
                "minOSVersion": "13.0",
            } for v in data["versions"]
        ],
    })

with open("source.json", "w", encoding="utf-8") as f:
    json.dump({
        "name": "dogt",
        "identifier": "com.leevip000.dogt",
        "apps": apps,
    }, f, indent=2, ensure_ascii=False)

# 生成每个软件的子订阅
for app in apps:
    sub = {
        "name": app["name"],
        "identifier": "com.leevip000.dogt." + app["name"],
        "apps": [app],
    }
    path = os.path.join(APPS_DIR, app["name"] + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sub, f, indent=2, ensure_ascii=False)

print("done")
