import json
import os
import requests
import shutil

# ----------------------------
# CONFIGURATION
# ----------------------------
MRPACK_DIR = "/Users/bevangelista/Downloads/cobbleverse_pack"   # directory where .mrpack is unzipped
OUTPUT_DIR = "/Users/bevangelista/Desktop/cobbleverse_pack"   # final server folder
SERVER_ZIP = "cobbleverse_server.zip"

# Fabric server settings
MINECRAFT_VERSION = "1.21.1"
FABRIC_LOADER_VERSION = "0.16.14"

# ----------------------------
# 1. Create server folder
# ----------------------------
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)
os.makedirs(os.path.join(OUTPUT_DIR, "mods"))

# ----------------------------
# 2. Install Fabric server loader
# ----------------------------
fabric_server_jar = os.path.join(OUTPUT_DIR, "fabric-server-launch.jar")
fabric_url = f"https://meta.fabricmc.net/v2/versions/loader/{MINECRAFT_VERSION}/{FABRIC_LOADER_VERSION}/server/json"

print(f"Downloading Fabric loader from {fabric_url}...")
r = requests.get(fabric_url)
r.raise_for_status()
with open(fabric_server_jar, "wb") as f:
    f.write(r.content)

# ----------------------------
# 3. Read modrinth.index.json and download mods
# ----------------------------
index_file = os.path.join(MRPACK_DIR, "modrinth.index.json")
with open(index_file) as f:
    index = json.load(f)

for mod in index["files"]:
    mod_path = mod["path"]
    if mod_path.startswith("mods/"):
        mod_filename = os.path.basename(mod_path)
        mod_url = mod["downloads"][0]
        dest_path = os.path.join(OUTPUT_DIR, "mods", mod_filename)
        print(f"Downloading {mod_filename}...")
        r = requests.get(mod_url, stream=True)
        r.raise_for_status()
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(r.raw, out)

# ----------------------------
# 4. Copy overrides folder
# ----------------------------
overrides_src = os.path.join(MRPACK_DIR, "overrides")
if os.path.exists(overrides_src):
    print("Copying overrides...")
    for item in os.listdir(overrides_src):
        s = os.path.join(overrides_src, item)
        d = os.path.join(OUTPUT_DIR, item)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, dirs_exist_ok=True)
            except PermissionError:
                print(f"⚠️ Skipping directory {s} due to permission error")
            except shutil.Error as e:
                print(f"⚠️ Error copying directory {s}: {e}")
        else:
            try:
                shutil.copy2(s, d)
            except PermissionError:
                print(f"⚠️ Skipping file {s} due to permission error")
# ----------------------------
# 5. Accept EULA
# ----------------------------
with open(os.path.join(OUTPUT_DIR, "eula.txt"), "w") as f:
    f.write("eula=true\n")

# ----------------------------
# 6. Zip the server folder
# ----------------------------
print(f"Creating server zip: {SERVER_ZIP}...")
shutil.make_archive(SERVER_ZIP.replace(".zip",""), 'zip', OUTPUT_DIR)

print("✅ Server ZIP ready!")
