#!/usr/bin/env python3
"""Generate ENTITY_MAP.md from the register definitions and translations.

The register YAML carries a human-facing ``description`` per entity; use it to
record the vendor-app label (e.g. "app: Workgroup Power") without renaming our
entities. This script turns that into a Markdown table that can be pasted into
release notes.

Usage:
    python tools/gen_entities_md.py            # write ENTITY_MAP.md
    python tools/gen_entities_md.py --stdout   # print instead of writing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "custom_components" / "dyness_modbus" / "registers" / "dyness.yaml"
EN_PATH = ROOT / "custom_components" / "dyness_modbus" / "translations" / "en.json"
OUT_PATH = ROOT / "ENTITY_MAP.md"
PREFIX = "<prefix>"

# (yaml section, platform, translation section, note)
SECTIONS = [
    ("SENSOR_DEFINITIONS", "sensor", "sensor", "polled from Modbus"),
    ("BINARY_SENSOR_DEFINITIONS", "binary_sensor", "binary_sensor", "polled from Modbus"),
    ("SELECT_DEFINITIONS", "select", "select", "writable"),
    ("SWITCH_DEFINITIONS", "switch", "switch", "writable"),
    ("NUMBER_DEFINITIONS", "number", "number", "writable"),
    ("BUTTON_DEFINITIONS", "button", "button", "action"),
    ("VERSION_SENSOR_DEFINITIONS", "sensor", "sensor", "computed"),
    ("EFFICIENCY_SENSOR_DEFINITIONS", "sensor", "sensor", "computed"),
    ("STORED_ENERGY_SENSOR_DEFINITIONS", "sensor", "sensor", "computed"),
    ("CYCLE_SENSOR_DEFINITIONS", "sensor", "sensor", "computed"),
    ("TOU_SENSOR_DEFINITIONS", "sensor", "sensor", "computed"),
]

COMPUTED_SECTIONS = {
    "VERSION_SENSOR_DEFINITIONS",
    "EFFICIENCY_SENSOR_DEFINITIONS",
    "STORED_ENERGY_SENSOR_DEFINITIONS",
    "CYCLE_SENSOR_DEFINITIONS",
    "TOU_SENSOR_DEFINITIONS",
}


def load() -> tuple[dict, dict]:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    translations = json.loads(EN_PATH.read_text(encoding="utf-8"))
    return data, translations.get("entity", {})


def describe(definition: dict) -> str:
    text = definition.get("description") or ""
    extra = []
    if "min" in definition or "max" in definition:
        extra.append(f"range {definition.get('min')}…{definition.get('max')}")
    if definition.get("step") is not None:
        extra.append(f"step {definition['step']}")
    if definition.get("options"):
        extra.append("options: " + ", ".join(definition["options"]))
    if definition.get("states"):
        extra.append(f"{len(definition['states'])} state labels")
    if extra:
        text = f"{text} ({'; '.join(extra)})" if text else "; ".join(extra)
    return text.replace("|", "/")


def rows_for(data: dict, translations: dict) -> list[str]:
    lines: list[str] = []
    for section, platform, trans_section, note in SECTIONS:
        definitions = data.get(section) or {}
        if not isinstance(definitions, dict) or not definitions:
            continue
        names = translations.get(trans_section, {})
        lines.append("")
        lines.append(f"### {platform} — {note}")
        lines.append("")
        lines.append("| Entity | Register | Type | Unit | Enabled | Description |")
        lines.append("|---|---|---|---|---|---|")
        entries = []
        for key, definition in definitions.items():
            definition = definition or {}
            register = definition.get("register")
            entries.append((register if register is not None else 10**9, key, definition))
        for register, key, definition in sorted(entries):
            name = (names.get(key) or {}).get("name", key)
            entity = f"`{platform}.{PREFIX}_{key}`"
            reg = "computed" if section in COMPUTED_SECTIONS else str(register)
            dtype = definition.get("data_type", "")
            if definition.get("count"):
                dtype += f" x{definition['count']}"
            unit = definition.get("unit") or ""
            enabled = "yes" if definition.get("enabled_by_default", True) else "no"
            lines.append(
                f"| {entity} | {reg} | {dtype} | {unit} | {enabled} | "
                f"{name} — {describe(definition)} |"
            )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = parser.parse_args()

    data, translations = load()
    body = rows_for(data, translations)

    header = [
        "# Dyness Aquavolt — entity map",
        "",
        "Generated from `custom_components/dyness_modbus/registers/dyness.yaml` and",
        "`translations/en.json` by `tools/gen_entities_md.py`. Do not edit by hand.",
        "",
        f"`{PREFIX}` is the device name slug chosen at setup (e.g. `M1`).",
    ]
    content = "\n".join(header + body) + "\n"

    if args.stdout:
        print(content)
    else:
        OUT_PATH.write_text(content, encoding="utf-8")
        print(f"wrote {OUT_PATH.relative_to(ROOT)} ({len(body)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
