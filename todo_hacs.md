# HACS Submission Checklist

This list tracks the necessary steps to prepare the **Wolf Climate Control ISM8** integration for submission to the HACS default repository.

## Hard Requirements (HACS Guidelines)
- [x] **Add LICENSE file:** A license file is mandatory for HACS. (e.g., MIT, Apache 2.0).
- [ ] **GitHub Repository Settings:**
    - [ ] Add description to the GitHub repository.
    - [ ] Add topics: `home-assistant`, `hacs`, `integration`, `wolf-heating`, `ism8`.
- [x] **Manifest Validation:**
    - [x] Fix trailing comma in `custom_components/wolf/manifest.json`.
    - [ ] Ensure all required fields are present.
- [x] **Minimum Home Assistant Version:**
    - [x] Add `"homeassistant": "2024.1.0"` (or later) to `hacs.json` as `runtime_data` is used.
- [ ] **README.md:** Ensure the README clearly describes what the integration does and how to install it.

## Quality & UX Improvements (Recommended)
- [ ] **Translations:** Complete entity-level translation keys in `translations/*.json` (referenced in `todo.md`).
- [ ] **Info.md:** Create an `info.md` file for better presentation within the HACS UI (optional but recommended).

## Repository Health
- [ ] **Release Tagging:** Ensure future versions are tagged as GitHub Releases (HACS uses these for versioning).
- [ ] **Pre-commit/Linting:** Add HACS/Home Assistant specific linting (e.g., `hassfest`, `hacs/action`).
