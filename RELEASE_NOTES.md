# Release notes — Dyness Aquavolt Modbus

Version scheme: `v<year>.<month>.<sequence>` where the sequence keeps increasing
within the month (e.g. `v2026.11.5` → `v2026.11.10`). The same number must be set
as `version` in `custom_components/dyness_modbus/manifest.json`; HACS compares
that field, not the git tag.

Newest release first.

---

## v2026.11.10 — TOU settings and power cap

*Prepared release — tag `v2026.11.10` (or `v2026.11.10-pr.1` pre-release).*

### Fixed
- **Version reporting**: `manifest.json` had been stuck at `2026.11.6`, so HACS
  never offered 11.7–11.9. Bumped, and `rell.bat` now refuses to run when the
  manifest version does not match its `VERSION`.
- **Firmware version** now matches the official Dyness app:
  `DSP1.DSP2.DSP-SVN-ARM.ARM-SVN` → devices report `17.0.269-10.238`. The format
  added in 11.8 printed `V17.0.10.13402` / `17.0.10-13402.238`.
- **Duplicate unique_id** on the Modbus connection binary sensor (defined both in
  the YAML and in Python).
- **Duplicate `ems_power_set`** entity (registered as both sensor and number).

### Added — TOU (economic mode)
- **Slots 1–4**, registers 27515–27530: start time, end time (HHMM), battery
  power in W (negative = charge, positive = discharge) and the weekday bitmask
  (`0xFF` high byte = enabled, bits 0–6 = Sunday…Saturday).
- **TOU schedule sensors** (`sensor.*_tou_schedule_1..4`) showing e.g.
  `19:20-03:04` with `start`, `end`, `days`, `enabled`, `power_w` attributes.
- **Force-charge SoC start/stop** (27531 / 27532).
- **Clear all economic mode** button (27533).
- **EMS power mode effective time** (27547) and **exit mode set** select (27548).
- **EMS modes 16 / 17** (Charge Only Self-use, Self-use) from protocol V1.15.
- **DSP SVN / ARM SVN** version sensors (registers 18 / 20).

### Added — general
- **Device name at setup**: the name becomes the entity-id prefix, so choosing
  `M1` yields `sensor.m1_battery_power`.
- **`rated_power`** (register 1) enabled by default.
- **`ENTITY_MAP.md`**, generated from the register definitions and including the
  vendor app labels as `app=...`.

### Changed
- **Breaking:** energy entities renamed from `*_to_grid_*` / `*_from_grid_*` to
  `utility_to_grid_*` / `utility_from_grid_*`. Re-point automations and the
  Energy dashboard.
- `EMS Power Set` is now −980…980 W (step 50, `int16`), capped at the inverter
  rated power (Power Level Setting) instead of ±2500.
- `TOU power` is signed watts, not a percentage. Verified against the app:
  register 27521 = −123 W is shown as “123 W, Charge”.
- Config entry title defaults to `Dyness Aquavolt` and is editable at setup.

### Docs
- Added a Home Battery Control package: `other-batteries/Dyness-Aquavolt/`
  (`marstek_m1_*` contract, helpers capped at 980 W).

### Testing
- 81 tests pass, including TOU decoding pinned to two real device dumps.

---

## v2026.11.9 — Documentation update

*Tag `V2026.11.9` (note the stray capital `V`).*

- Refreshed `README.md`, `SETUP_GUIDE.md` and `RELEASE_NOTES.md`.
- No code change.
- **Manifest was not bumped** (still `2026.11.6`), so HACS did not offer this
  update.

---

## v2026.11.8 — Modbus connection sensor

- Added the `modbus_connection` diagnostic binary sensor, exposing connection
  health (`ok` / `degraded` / `offline`, last successful read, block timeouts).
- Introduced a `dsp_arm_bms_modbus` version mode
  (`dsp1.dsp2.arm-bms.modbus`). This was **wrong** and is superseded by
  2026.11.10 — it printed `17.0.10-13402.238` instead of `17.0.269-10.238`.
- Fixed a misplaced brace in `translations/en.json` that broke loading.
- **Manifest was not bumped** (still `2026.11.6`) — not visible in HACS.

---

## v2026.11.7 — Register descriptions and TOU registers

- Added a `description` field to every register definition.
- First TOU implementation: registers 27515–27533. The first read of these was
  based on the protocol table only and turned out to be wrong (see 2026.11.10):
  power is signed watts, `27531`/`27532` are force-charge SoC thresholds, and
  `27533` is “clear all economic mode”, not an exit-mode setting.
- Renamed `energy_to_grid_*` / `energy_from_grid_*` to `utility_to_grid_*` /
  `utility_from_grid_*`.
- Added brand icons, `run_tests.bat`, `tests/pytest.bat`; removed leftover
  kilo.ai scripts.
- **Manifest was not bumped** (still `2026.11.6`) — not visible in HACS.

---

## v2026.11.6 — Scan interval optimization

- Added a **medium** scan tier (30 s) between high (10 s) and low (60 s). Only
  five entities still poll at 10 s: AC active power, utility power phase 1, AC
  port backup power, battery power, battery mode.
- Repaired `translations/en.json`: removed a duplicated `entity` block and moved
  the `*_RO` keys from `entity.number` to `entity.sensor`, which fixed
  “unexpected end of data” during integration setup.
- Added the test suite (`pytest.ini`, `requirements_test.txt`, decoding / setup /
  config-flow / client / simulator / JSON-validation tests — 46 at the time).
- Removed leftover helper scripts from the repository root.

---

## v2026.11.5 — Power register decoding

- **Power registers changed from S32 to S16**: the inverter reports registers
  120, 125, 130, 133, 135, 137, 143, 268, 272, 276, 385 as 4-byte values where
  the first 2 bytes are ignored. Previous versions decoded them as `int32`,
  producing values such as `196608 W` instead of `3 W`.
- **Phase naming**: AC port and utility registers renamed from R/S/T to
  Phase 1/2/3.
- **EMS Power Mode select** (27511) with Charge-BAT (0x000B) and Discharge-BAT
  (0x000C) modes, and **EMS Power Set** number (27512).
- Read-only debug sensors (disabled by default): `ems_power_set_RO`,
  `ems_power_mode_RO`, `operation_mode_RO`, `feed_power_para_RO`,
  `batt_charge_curr_max_RO`, `batt_discharge_curr_max_RO`, and the experimental
  `router_*` / `manufacturer_RO`.
- Added temperature and bus sensors, `port_number_1` / `modbus_address` /
  `modbus_baud_rate`, and the safety-country state mapping (107 codes).
- Template sensors for Home Battery Control documented in the README.
- Removed `pymodbus` from `requirements.txt` (Home Assistant provides it).

---

## Earlier releases

| Tag | Manifest | Note |
|---|---|---|
| `v2026.11.2` | 2026.11.1 | initial public drop |
| `v2026.11.3` | 2026.11.1 | AC port backup power, `power_ratio` decoding, EMS modes |
| `v2026.11.4` | 2026.11.4 | Marstek component removed from the package |

`.2` and `.3` also shipped a manifest version that did not match their tag.
