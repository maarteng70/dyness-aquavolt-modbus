# Working agreement for this repository

Conventions to follow whenever the Dyness Aquavolt integration is changed or
released. Keep this file updated when the process changes.

## Releases

1. **Always propose a release name and tag first, and wait for confirmation.**
   - Suggest one short release name (Title Case, e.g. `TOU settings`,
     `Firmware string fix`) that summarises the change set.
   - Suggest the matching tag (`v<manifest version>`, plus a `-pr.N` variant for
     a pre-release).
   - Do not edit `rell.bat`, bump the manifest, or produce release notes until
     the name is confirmed.
2. `rell.bat` **never creates or pushes tags.** It only checks whether the
   suggested tag is free and prints instructions.
3. `VERSION` in `rell.bat` must equal `version` in
   `custom_components/dyness_modbus/manifest.json`. HACS compares the manifest
   version, not the git tag — a stale manifest makes releases invisible.
4. `rell.bat` regenerates `ENTITY_MAP.md` (step 2b) before committing.
5. Release notes are printed by `rell.bat` and pasted into the GitHub release;
   the GitHub release title is the release name, not the tag.
6. **Version scheme:** `v<year>.<month>.<sequence>`, e.g. `v2026.11.5`, and the
   sequence only ever increases within the month (`v2026.11.10` follows
   `v2026.11.9`). Always lowercase `v`.
7. **Every time `rell.bat` is prepared, add the release to `RELEASE_NOTES.md`**
   (newest first) with the confirmed release title, e.g.
   `## v2026.11.10 — TOU settings and power cap`. `rell.bat` fails if that
   heading is missing.
8. Keep `manifest.json`, `RELEASE_NOTES.md` and `rell.bat`'s `VERSION` in sync;
   all three describe the same release.

## Entity naming

- Use our own consistent names (`tou_start_time_1`, `ems_power_set`, ...).
- Do **not** rename entities after the vendor app's wording.
- Record the vendor label in the register `description` using the parseable
  token `app=<label>`, e.g.
  `description: TOU slot 2 battery power in W (negative = charge); app=Power`
- `tools/gen_entities_md.py` turns those descriptions into `ENTITY_MAP.md`.

## Register knowledge

- Verify register meaning against `dyness_hybrid_modbus_protocol_v1.15.md`
  **and** a real device dump in `mydevice/` before relying on it.
- New dumps: `python mydevice\modbus_dump.py --host <ip> --read-timeout 3 --delay 0.15`
- Compare two dumps: `python mydevice\dump_diff.py <old> <new>`
- Known firmware facts (Aquavolt D2.5-LAC, host `17.0.269-10.238`):
  - rated power (reg 1) = 980 W; all power control must be capped at this
  - TOU power (27517/27521/27525/27529) is **signed watts**, negative = charge
  - TOU weekday mask: high byte `0xFF` = enabled, bits 0-6 = Sun..Sat
  - registers 2026 and the whole `25xxx` block time out (not implemented)
  - `27531`/`27532` (force-charge SoC) read `0xFFFF` when unused

## Testing

- `python -m pytest tests\ -q` must pass before a release (currently 81 tests).
- Tests that pin decoded values should reference a real dump and say which one.

## Breaking changes

- Entity-ID renames are acceptable while the integration is in pre-release, but
  they must be listed under "Breaking" in the release notes.
