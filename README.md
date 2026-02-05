# Home Assistant Unique ID Patch Addon

This Home Assistant Addon allows you to manually modify the `Unique ID` of Config Entries in `core.config_entries`.
It is primarily designed to resolve **"Already configured"** errors when adding multiple ONVIF cameras that share the same MAC address due to firmware bugs.

![Screenshot](https://placeholder.com/screenshot.png)

## Why do I need this?

Some IP cameras (ONVIF) report a fixed/duplicate MAC address (e.g., `00:30:1b:ba:02:db`) via the ONVIF protocol, even if their physical NIC has a unique MAC.
Home Assistant's ONVIF integration uses this reported MAC as the Unique ID.
- **Device A** registers successfully (ID: `00...db`).
- **Device B** attempts to register, reports the same `00...db`, and HA rejects it as "Already configured", failing to recognize it as a new device.

This addon lets you **rename Device A's ID** (e.g., to `...db-1`), freeing up the original ID so Device B can be registered.
*Note: Home Assistant treats duplicated Unique IDs as the same device.*

## Features

- **List Entries**: View all Config Entries and their current Unique IDs.
- **Manual Edit**: Manually edit any Unique ID to resolve conflicts.
- **MAC Address Sync**: Update the Unique ID to match the *detected* MAC address (from `core.device_registry`).
- **Title Update**: Automatically append the ID to the device title for easier identification.
- **Multi-language**: Supports English and Japanese.

## How to Use

1.  **Install & Start**: Install the addon and start it. Open the Web UI.
2.  **Find the Conflict**: Locate the entry that is causing conflicts.
3.  **Edit ID**:
    - Enter a new, unique string in the text box (e.g., add `-1` to the end).
    - Click **Update**.
4.  **Restart HA**: Restart Home Assistant Core to apply changes.

### ⚠️ Important: About "Mac Addr Sync" Button

This button syncs the Unique ID with the MAC address detected by Home Assistant.
**Use with caution:**

*   **✅ SAFE**: If your device info in Home Assistant shows a **correct, unique MAC address** (e.g., MAC: `xx:xx:xx:xx:xx:xx`), using this button is safe and recommended to fix mismatched IDs.
*   **❌ UNSAFE**: If your devices are suffering from the "Same MAC" bug (e.g., multiple cameras all showing MAC: `00:30:1b:ba:02:db`), **DO NOT USE THIS BUTTON**. It will set them all to the same ID, causing conflicts again. **Obtain the correct MAC address by some means and perform a Manual Edit.**

## Installation

1.  Copy this repository to your local add-ons folder or add it as a repository in the Add-on Store.
2.  Install "HA Unique ID Patch".
3.  Start the addon.
4.  Disable "Protection mode" may be required if the addon needs deep access (though this version primarily operates on config files mapped to `/config`).

## Disclaimer

This addon directly modifies Home Assistant's internal storage files (`/config/.storage/core.config_entries`).
**Modifying core configuration files is high-risk and can lead to file corruption or Home Assistant failing to start.**

While we take safety seriously by **automatically creating a timestamped backup** (e.g., `core.config_entries.bak_YYYYMMDD_HHMMSS`) in the same `.storage` directory before every write, this is not a substitute for a full system backup.

**ALWAYS PERFORM A FULL HOME ASSISTANT BACKUP BEFORE USE.**
The author is not responsible for any data corruption or system failure.
