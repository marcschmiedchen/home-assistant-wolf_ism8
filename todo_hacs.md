# HACS Submission Checklist

This list tracks the necessary steps to prepare the **Wolf Climate Control ISM8** integration for submission to the HACS default repository.

## Hard Requirements (HACS Guidelines)
- [x] **Add LICENSE file:** A license file is mandatory for HACS. (e.g., MIT, Apache 2.0).
- [ ] **GitHub Repository Settings (MANUAL ACTION REQUIRED):**
    - [x] Add description to the GitHub repository.
    - [x] Add topics: `home-assistant`, `hacs`, `integration`, `wolf-heating`, `ism8`.
- [x] **Manifest Validation:**
    - [x] Fix trailing comma in `custom_components/wolf/manifest.json`.
    - [x] Ensure all required fields are present.
- [x] **Minimum Home Assistant Version:**
    - [x] Add `"homeassistant": "2024.1.0"` (or later) to `hacs.json` as `runtime_data` is used.
- [x] **README.md:** Ensure the README clearly describes what the integration does and how to install it. (Now Bilingual)

## Quality & UX Improvements (Recommended)
- [ ] **Translations:** Complete entity-level translation keys (Skipped for now).
- [x] **Info.md:** Create an `info.md` file for better presentation within the HACS UI (optional but recommended).

## Repository Health
- [x] **Release Tagging:** Ensure future versions are tagged as GitHub Releases (HACS uses these for versioning).
- [x] **Pre-commit/Linting:** Add HACS/Home Assistant specific linting (e.g., `hassfest`, `hacs/action`).

## Submission Process
1. [ ] **Fork the HACS Default Repository:** Fork [hacs/default](https://github.com/hacs/default).
2. [ ] **Edit `integrations.json`:** Add `"marcschmiedchen/home-assistant-wolf_ism8"` to the list.
3. [ ] **Sort Alphabetically:** Ensure the list in `integrations.json` is still sorted alphabetically by repository name (or domain, follow existing pattern).
4. [ ] **Submit Pull Request:** Create a PR to the HACS default repository.
5. [ ] **Wait for Bot:** The HACS bot will run validations and provide feedback.
