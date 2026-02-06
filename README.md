# HA Unique ID Patch Addon

This Home Assistant Addon allows you to manually modify the `Unique ID` of Config Entries in `core.config_entries`.
It is primarily designed to resolve **"Already configured"** errors when adding multiple ONVIF cameras that share the same MAC address due to firmware bugs.

## Specific Issues and Solutions

Some IP cameras (ONVIF) report a fixed/duplicate MAC address (e.g., `00:30:1b:ba:02:db`) via the ONVIF protocol, even if their physical NIC has a unique MAC.
Home Assistant's ONVIF integration uses this reported MAC as the Unique ID.
- **Device A** registers successfully (ID: `00...db`).
- **Device B** attempts to register, reports the same `00...db`, and HA misidentifies it as "Device A". It fails to recognize it as a new device and shows **"Already configured"**.

This addon lets you **rename Device A's ID** (e.g., to `...db-1`), freeing up the original Unique ID space so Device B can be registered.
*Note: Due to Home Assistant's specifications, if Unique IDs conflict, they are registered as the same device.*
<img width="1049" height="918" alt="image" src="https://github.com/user-attachments/assets/6a99ca67-c62c-46d9-9f5d-aed4643bb80c" />
<img width="1013" height="798" alt="image" src="https://github.com/user-attachments/assets/51844da5-fd02-4174-a144-b8f2cb6917bf" />



## Features

- **List Entries**: View all Config Entries and their current Unique IDs.
- **Manual Edit**: Manually edit any Unique ID to resolve conflicts.
- **MAC Address Sync**: Update the Unique ID to match the *detected* MAC address (from `core.device_registry`).
- **Japanese/English support**: Supports both English and Japanese.

## How to Use

1.  **Install & Start**: Install the addon and start it. Open the Web UI.
2.  **Find the Conflict**: Locate the entry that is causing conflicts.
3.  **Edit ID**:
    - For conflict avoidance: Enter a new, unique string in the text box (e.g., add `-1` to the end).
    - Click **Update**.
4.  **Restart HA**: Restart Home Assistant Core to apply changes.

### ⚠️ Important: About "Mac Addr Sync" Button

This button syncs the Unique ID with the MAC address detected by Home Assistant.
**Use with caution depending on the situation:**

*   **✅ RECOMMENDED**: If the MAC address for the target camera (ONVIF) is **displayed correctly (e.g., MAC: `xx:xx:xx:xx:xx:xx`)** in the Home Assistant device information screen.
    *   Clicking this button is recommended as it allows you to correct the ID to the proper MAC address.
*   **❌ FORBIDDEN**: If the target camera displays **the same MAC address as other cameras (e.g., MAC: `00:30:1b:ba:02:db`)**.
    *   **DO NOT USE THIS BUTTON.** The IDs will conflict again, resulting in an error. Obtain the correct MAC address by some other means and perform a manual edit.

### About Actual Behavior

This addon operates by stopping the Home Assistant Core in the background (changes are not reflected unless stopped), directly modifying the configuration files, and then restarting the Core.
Therefore, the changes are persistent and will not revert even after restarting Home Assistant.

## Installation

1.  Copy this repository to your local add-ons folder or add it as a repository in the Add-on Store.
2.  Install "HA Unique ID Patch".
3.  Start the addon.
4.  Access to the `/config` directory is required.

## Disclaimer

This addon directly modifies Home Assistant's internal setting files (`/config/.storage/core.config_entries`).
**Modifying core configuration files is high-risk and can lead to file corruption or Home Assistant failing to start.**

While we take safety seriously by **automatically creating a timestamped backup** (e.g., `core.config_entries.bak_20260206_015000`) in the same `.storage` directory before every write, this is not a substitute for a full system backup.

**ALWAYS PERFORM A FULL HOME ASSISTANT BACKUP BEFORE USE.**
The author is not responsible for any data corruption or system failure.
