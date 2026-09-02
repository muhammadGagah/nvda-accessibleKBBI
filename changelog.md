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
