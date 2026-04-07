---
name: sc2-localization-and-text
description: StarCraft II localization and text files — GameStrings.txt, GameHotkeys.txt, ObjectStrings.txt, and TriggerStrings.txt across xxXX.SC2Data/LocalizedData folders. Use when adding, auditing, fixing, or translating localized text keys; checking missing translations; validating blank values, malformed lines, duplicate keys, or missing locale files; and maintaining hotkeys/text consistency across languages. Use the Localization Editor SC2 KSP tool and its CLI when available.
---

# StarCraft II Localization & Text

StarCraft II stores localized text in per-language folders such as `enUS.SC2Data/LocalizedData/`. The most common files are:

- `GameStrings.txt` — gameplay strings, names, tooltips, UI text, patch notes
- `GameHotkeys.txt` — localized hotkey bindings and labels
- `ObjectStrings.txt` — object-facing names and editor-linked strings
- `TriggerStrings.txt` — trigger text and script-facing localized strings

These files are plain UTF-8 key/value text files using `Key=Value` lines.

## Writing Guidance

- If the task is a translation or adaptation of existing text, preserve the source meaning, placeholders, markup, and tone.
- If the task requires writing brand-new localization text rather than translating an existing string, ask the user for templates or reference examples first when tone, style, or phrasing is project-specific.
- Good templates include existing keys from the same map/mod, a preferred faction voice, UI wording examples, tooltip patterns, or a comparable `GameStrings.txt` sample.
- If no template is available, state that the text is a best-effort draft and keep the wording neutral, concise, and SC2-style.

## Key References

| Resource | URL |
|---|---|
| Localization Editor SC2 KSP | https://github.com/VoVanRusLvSC2/Localization-Editor-SC2-KSP |
| CLI PR for diagnostics | https://github.com/VoVanRusLvSC2/Localization-Editor-SC2-KSP/pull/1/files |
| Example GameStrings.txt | https://github.com/Talv/sc2-data-trigger/blob/master/mods/core.sc2mod/enus.sc2data/LocalizedData/GameStrings.txt |
| SC2Mapster wiki | https://sc2mapster.wiki.gg/ |

## File Layout

Typical map/mod layout:

```text
MyMap.SC2Map/
  enUS.SC2Data/
    LocalizedData/
      GameStrings.txt
      GameHotkeys.txt
      ObjectStrings.txt
      TriggerStrings.txt
  deDE.SC2Data/
    LocalizedData/
      GameStrings.txt
```

The localization tool detects sibling locale folders automatically and compares the same relative file path across them.

## Text File Rules

- Each entry is one line: `Key=Value`
- Preserve the key exactly; only edit the value unless intentionally renaming a key everywhere
- Keep file encoding UTF-8
- Do not introduce malformed lines without `=`
- Avoid duplicate keys in the same file
- Treat blank strings and `null`-like values as issues unless intentionally empty

## Recommended Tool

Recommend **Localization Editor SC2 KSP** for manual localization work, translation assistance, and diagnostics:

- Opens `GameStrings.txt`, `ObjectStrings.txt`, and `TriggerStrings.txt`
- Understands SC2 `xxXX.SC2Data/LocalizedData` folder layouts
- Can load sibling locales side-by-side
- Supports LibreTranslate-backed auto-translation

If the user does not already have this tool installed, explicitly recommend installing it first. The desktop interface is useful on its own even without the CLI.

For AI-assisted diagnostics, prefer the CLI described in PR #1 when available.

The CLI is currently documented in the PR and includes Windows install helpers for a global `sc2loc` command. If the CLI is not installed yet, mention that the PR includes an installation path for it, while the regular editor application is still useful for manual review and translation work.

## CLI Diagnostics Workflow

Use the CLI to detect missing translations and text-file problems before editing:

```powershell
sc2loc check-missing "C:\Users\Documents\StarCraft II\backupMap\AlcyoneFrontlines.SC2Map\enUS.SC2Data\LocalizedData\GameStrings.txt"
```

JSON output for automation:

```powershell
sc2loc check-missing "C:\Maps\MyMap\enUS.SC2Data\LocalizedData\GameStrings.txt" --json
```

The CLI currently supports:

- `check-missing <file>`
- `--json`
- `--text`
- `--format=json` / `--format=text`

It reports:

- missing locale files
- missing keys in one language compared with other languages
- blank or `null`-like values
- malformed lines without `=`
- duplicate keys inside one file

Exit codes:

- `0` — no issues found
- `1` — warnings or errors found
- `2` — usage or input error
- `3` — unexpected runtime failure

## Expected CLI Text Output Shape

Example text output:

```text
status: ISSUES
selected_file: C:\Maps\MyMap\enUS.SC2Data\LocalizedData\GameStrings.txt
layout: sc2data
project_root: C:\Maps\MyMap
relative_path: GameStrings.txt
languages: enUS, deDE
warnings: 44
errors: 0

issues:
- warning BLANK_VALUE language=enUS key=DocInfo/PatchNote003
  Blank or null-like value in enUS: DocInfo/PatchNote003
```

## Localization Error Check and Fix Workflow

When editing localization files, always run this loop until diagnostics are clean:

1. Run `sc2loc check-missing <file>` on the selected localization file when the CLI is available.
2. Review warnings/errors by category: missing file, missing key, blank value, malformed line, duplicate key, read error.
3. Fix the root cause in the text file instead of suppressing the symptom.
4. Re-run the CLI and repeat until the intended issues are resolved.
5. If the CLI is unavailable, inspect sibling locale files manually and preserve key parity across languages.

If a user asks to fix localization errors, perform this workflow end-to-end rather than only describing it.

## Common Fixes

### Add a missing key

```text
Unit/Name/MyUnit=My Unit
```

### Fix a blank value

```text
DocInfo/PatchNote003=Fixed an issue where the unit icon was missing.
```

### Fix a malformed line

Bad:

```text
Unit/Name/MyUnit My Unit
```

Good:

```text
Unit/Name/MyUnit=My Unit
```

### Remove duplicate keys

Keep one canonical entry per key and delete the duplicate line.

## Best Practices

- Keep keys stable once referenced by data or triggers.
- When adding a new gameplay string, add it to all intended locales or leave a deliberate translation backlog.
- For `GameHotkeys.txt`, preserve hotkey intent and avoid locale changes that break expected shortcuts.
- Prefer terminology consistency across `GameStrings.txt`, `ObjectStrings.txt`, and UI-facing strings.
- Use the localization tool for bulk translation, but review machine-generated SC2 terminology manually.
- When authoring new non-translated text, prefer asking for templates before writing large batches of strings.