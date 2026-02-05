import os
import json
import shutil
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

TRANSLATIONS = {
    "ja": {
        "title": "HA Unique ID Patch",
        "alert": "⚠ 注意: IDを変更した後は、Home Assistant本体を再起動する必要があります。書き換え前に自動的にバックアップが保存されます。",
        "current_id": "現在のID",
        "placeholder": "新しいUnique IDを入力...",
        "sync_mac": "Mac Addr同期",
        "update_title": "タイトルも更新",
        "bulk_top": "選択した項目を一括更新",
        "bulk_bottom": "選択した項目を一括更新",
        "result_title": "更新完了",
        "result_msg": "{n} 件の変更を保存しました。",
        "result_note": "変更を反映させるには、Home Assistant の再起動が必要です。",
        "back_home": "ホームに戻る",
        "restart_btn": "今すぐ再起動する", # Removed from UI but keeping key just in case
        "lang_switch": "English"
    },
    "en": {
        "title": "HA Unique ID Patch",
        "alert": "⚠ CAUTION: You must restart Home Assistant after changing IDs. A backup is automatically saved before modification.",
        "current_id": "Current ID",
        "placeholder": "Enter new Unique ID...",
        "sync_mac": "Sync Mac Addr",
        "update_title": "Update Title",
        "bulk_top": "Update Selected",
        "bulk_bottom": "Update Selected",
        "result_title": "Update Complete",
        "result_msg": "Saved {n} changes.",
        "result_note": "A Home Assistant restart is required to apply changes.",
        "back_home": "Back to Home",
        "restart_btn": "Restart Now",
        "lang_switch": "日本語"
    }
}

app = Flask(__name__)
print(f"[{datetime.now()}] Flask Info: App initialized.")

# Home Assistant の設定ディレクトリ（アドオンからは /config にマウントされる）
CONFIG_PATH = "/config"
if os.path.isdir(CONFIG_PATH):
    print(f"[{datetime.now()}] Config Info: {CONFIG_PATH} exists.")
    print(f"[{datetime.now()}] Config Info: Contents: {os.listdir(CONFIG_PATH)[:5]}...")
else:
    print(f"[{datetime.now()}] Config Warning: {CONFIG_PATH} does not exist!")

STORAGE_DIR = os.path.join(CONFIG_PATH, ".storage")
ENTRIES_FILE = os.path.join(STORAGE_DIR, "core.config_entries")
DEVICES_FILE = os.path.join(STORAGE_DIR, "core.device_registry")

def get_json_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_entries():
    return get_json_file(ENTRIES_FILE)

def get_devices():
    return get_json_file(DEVICES_FILE)

def find_mac_for_entry(entry_id, devices_data):
    if not devices_data:
        return None
    for device in devices_data.get("data", {}).get("devices", []):
        if entry_id in device.get("config_entries", []):
            for conn in device.get("connections", []):
                if conn[0] == "mac":
                    return conn[1]
    return None

def save_entries(data):
    # バックアップの作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{ENTRIES_FILE}.bak_{timestamp}"
    shutil.copy2(ENTRIES_FILE, backup_file)
    
    # 書き込み
    with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    lang = request.args.get("lang", "ja")
    if lang not in TRANSLATIONS:
        lang = "ja"

    data = get_entries()
    if not data:
        return "core.config_entries not found. Ensure /config is correctly mapped.", 404
    
    entries = data.get("data", {}).get("entries", [])
    
    # Enrich entries with detected MAC address from device registry
    devices_data = get_devices()
    for entry in entries:
        entry["detected_mac"] = find_mac_for_entry(entry["entry_id"], devices_data)

    # ドメインでソート
    entries.sort(key=lambda x: x.get("domain", ""))
    
    return render_template("index.html", entries=entries, texts=TRANSLATIONS[lang], current_lang=lang)

@app.route("/update_bulk", methods=["POST"])
def update_bulk():
    data = get_entries()
    if not data:
        return "Failed to load entries", 500

    sync_mac_ids = request.form.getlist("sync_mac_ids")
    update_title_ids = request.form.getlist("update_title_ids")
    
    devices_data = get_devices() # Always load devices as we don't know if needed beforehand easily
    
    updated_count = 0
    entries_list = data.get("data", {}).get("entries", [])

    print(f"[INFO] Bulk Update Requested. Sync MACs: {len(sync_mac_ids)}, Title Updates: {len(update_title_ids)}")

    for entry in entries_list:
        entry_id = entry.get("entry_id")
        changed = False
        new_unique_id = None
        
        # 1. Determine New Unique ID
        if entry_id in sync_mac_ids:
            # Try to get MAC from device registry
            mac = find_mac_for_entry(entry_id, devices_data)
            if mac:
                new_unique_id = mac
                print(f"[INFO] {entry_id}: Syncing MAC -> {mac}")
        
        # If not syncing MAC (or MAC not found), check manual input
        if not new_unique_id:
             # Form input name is "new_id_<entry_id>"
            manual_input = request.form.get(f"new_id_{entry_id}")
            if manual_input and manual_input != entry.get("unique_id"):
                 new_unique_id = manual_input
                 print(f"[INFO] {entry_id}: Manual Update -> {manual_input}")

        # 2. Apply Unique ID Change
        if new_unique_id and new_unique_id != entry.get("unique_id"):
            entry["unique_id"] = new_unique_id
            changed = True

        # 3. Apply Title Update (Only if requested AND ID was valid)
        # Note: Title update logic relies on the *current* (potentially just updated) ID
        if entry_id in update_title_ids:
            current_id = entry.get("unique_id") # Use the latest ID
            current_title = entry.get("title", "")
            
            # Format: "Name - ID"
            if " - " in current_title:
                base_name = current_title.rsplit(" - ", 1)[0]
                entry["title"] = f"{base_name} - {current_id}"
            else:
                entry["title"] = f"{current_title} - {current_id}"
            
            # Even if only title changed (e.g. ID was same but title format update requested), we mark as changed
            if entry["title"] != current_title:
                changed = True
                print(f"[INFO] {entry_id}: Title Updated -> {entry['title']}")

        if changed:
            updated_count += 1

    lang = request.form.get("lang", "ja")
    if lang not in TRANSLATIONS:
        lang = "ja"

    if updated_count > 0:
        save_entries(data)
        print(f"[INFO] Saved {updated_count} changes.")
        msg = TRANSLATIONS[lang]["result_msg"].format(n=updated_count)
        return render_template("restart_confirm.html", changes_msg=msg, texts=TRANSLATIONS[lang], current_lang=lang)
    else:
        print("[INFO] No changes detected.")
        return redirect(url_for('index', lang=lang))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)

