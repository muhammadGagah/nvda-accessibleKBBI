# Version 1.4.0

## Compatibility

- Tested with NVDA 2026.3. The minimum supported NVDA version remains 2024.1.

## New Features

- **Suggestions** (Saran): lists KBBI words that start with the text in the search field, up to 100, using the KBBI API search endpoint. Choose a word to look it up.
- When a word is not found, the result area lists similar words. If the full word has no matches, the last one or two letters are trimmed, so a typo such as "rumh" still suggests "rumah".
- **Related words** (Kata Terkait): lists the base word, referenced words, variants, non-standard forms, derived words, and compound words of the current result. Choose one to look it up without retyping it.
- Results now show non-standard forms (bentuk tidak baku), variants (varian), and entry variants (varian entri).
- Precategorical entries (prakategorial), which have no definition of their own, now explain this and point to their derived words instead of showing only the headword.
- New **Show full label names** checkbox (Tampilkan nama label lengkap) shows labels such as "Nomina" and "Cakapan" instead of "n" and "cak". The choice is saved.

## Fixes

- Focus stays on the Suggestions button while suggestions load, so it returns there when the list closes.
- The Mark button is now announced as a button. It was a toggle button, so NVDA read it as a check box, and after marking it said "Hapus Tanda check box checked", repeating the state that the new label already gives.
- The History and Favorites lists no longer cut off their buttons. The Close button was hidden on displays with scaling above 100%. Both dialogs now size themselves from their contents and scale with Windows display settings, without exceeding the screen.
- Search results now show metaphors (kiasan). They were downloaded from KBBI but never displayed.
- Searching for text that contains a slash (`/`) now looks up that text instead of a different API path.
- Results no longer fail with an internal error when the KBBI service adds or removes label fields.
- History and favorites are written to a temporary file first, so an interrupted save can no longer leave the file empty or truncated.
- The add-on now uses the translation catalog set up by NVDA instead of wxPython's, so future translations of the add-on will load.

# Version 1.3

## Compatibility and Shortcuts

- Updated and tested the add-on metadata for NVDA 2026.2.
- Kept the minimum supported NVDA version at 2024.1.
- Changed the dialog shortcut to `NVDA+Windows+K`.
- Changed selected-text search to `NVDA+Windows+Shift+K`.
- Removed the previous shortcut assignment that conflicted with an NVDA command.

## Dialog and Focus Behavior

- Improved first-open and reopen focus using NVDA popup lifecycle handling.
- Added reliable foreground activation and delayed focus for the search field.
- Fixed selected-text search being ignored when the KBBI dialog was already open.
- Restored focus to the application and control used before opening the KBBI dialog.
- Added a visible label and reliable Enter and Escape handling to history and favorites lists.
- Ensured temporary and confirmation dialogs are always destroyed safely.

## Search and Results

- Prevented older asynchronous requests from overwriting newer search results.
- Improved result and error announcements and moved focus to readable output when appropriate.
- Improved reopening and reuse of the existing KBBI window.
- Preserved selected-text search behavior across supported browsers, editors, and terminals.

## Favorites and Configuration

- Changed the favorite action to a native toggle button with synchronized checked state.
- Improved favorite state updates when items are added or removed.
- Guarded configuration writes with `NVDAState.shouldWriteToDisk()`.

## Build and Packaging

- Removed the invalid `updateChannel = "None"` manifest entry when no update channel is configured.
- Added quoted manifest values together with source URL and license metadata.
- Excluded Python cache files from release packages.
- Fixed the add-on build helper source-suffix configuration.
