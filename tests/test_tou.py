"""Tests for the TOU (economic mode) schedule helpers.

Values are taken from the real device dump
mydevice/modbus_dump_20261121_140537.txt so the decoding is pinned to
hardware that is known to work:

  27515 StartTime_1 = 200   -> 02:00
  27516 EndTime_1   = 621   -> 06:21
  27517 Percent_1   = -400
  27518 WorkWeek_1  = 65376 -> 0xFF60 -> enabled, Fri + Sat
  27519 StartTime_2 = 1100  -> 11:00
  27520 EndTime_2   = 1400  -> 14:00
  27526 WorkWeek_3  = 4     -> 0x0004 -> disabled, Tuesday
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Load the helper module directly by path. Importing the package would pull in
# custom_components/dyness_modbus/__init__.py, which needs Home Assistant.
_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "dyness_modbus"
    / "helpers"
    / "tou.py"
)
_spec = importlib.util.spec_from_file_location("dyness_tou", _MODULE_PATH)
_tou = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tou)

DAY_NAMES = _tou.DAY_NAMES
describe_schedule = _tou.describe_schedule
format_hhmm = _tou.format_hhmm
schedule_label = _tou.schedule_label
week_days = _tou.week_days
week_enabled = _tou.week_enabled


class TestFormatHhmm:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            (200, "02:00"),
            (621, "06:21"),
            (1100, "11:00"),
            (1400, "14:00"),
            (701, "07:01"),
            (943, "09:43"),
            (1631, "16:31"),
            (2003, "20:03"),
            (0, "00:00"),
            (2359, "23:59"),
        ],
    )
    def test_valid_values(self, raw, expected):
        assert format_hhmm(raw) == expected

    @pytest.mark.parametrize("raw", [None, "unknown", "unavailable", ""])
    def test_non_numeric(self, raw):
        assert format_hhmm(raw) is None

    @pytest.mark.parametrize("raw", [-1, 2400, 2360, 9999, 65535])
    def test_out_of_range(self, raw):
        assert format_hhmm(raw) is None


class TestWeekMask:
    def test_dump_slot_1_friday_saturday(self):
        assert week_enabled(65376) is True
        assert week_days(65376) == ["Fri", "Sat"]

    def test_dump_slot_3_disabled_tuesday(self):
        assert week_enabled(4) is False
        assert week_days(4) == ["Tue"]

    def test_all_days(self):
        # 0xFF7F = enabled, every day
        assert week_enabled(0xFF7F) is True
        assert week_days(0xFF7F) == DAY_NAMES

    def test_sunday_bit(self):
        assert week_days(0xFF01) == ["Sun"]

    def test_no_days(self):
        assert week_days(0xFF00) == []

    def test_none(self):
        assert week_days(None) == []
        assert week_enabled(None) is False


class TestDescribeSchedule:
    def test_dump_slot_1(self):
        d = describe_schedule(200, 621, -400, 65376)
        assert d["start"] == "02:00"
        assert d["end"] == "06:21"
        assert d["enabled"] is True
        assert d["days"] == ["Fri", "Sat"]
        assert d["days_text"] == "Fri, Sat"
        assert d["power_w"] == -400
        assert d["raw"]["week"] == 65376

    def test_label_enabled(self):
        assert schedule_label(200, 621, 65376) == "02:00-06:21"

    def test_label_disabled(self):
        assert schedule_label(1100, 1400, 4) == "11:00-14:00 (off)"

    def test_label_invalid_time(self):
        assert schedule_label(65535, 621, 65376) is None


def test_dump_values_round_trip():
    """Every TOU slot in the dump must decode to a plausible clock time."""
    dump_slots = [
        (200, 621, -400, 65376),
        (1100, 1400, -400, 65344),
        (701, 943, 600, 4),
        (1631, 2003, 800, 65344),
    ]
    for start, end, power, week in dump_slots:
        d = describe_schedule(start, end, power, week)
        assert d["start"] is not None
        assert d["end"] is not None
        assert d["power_w"] == power


def test_dump_20261128_slot2_matches_vendor_app():
    """Slot 2 as shown in the vendor app: 19:20-03:04, 123 W charge, Monday.

    Values taken from modbus_dump_20261128_115854.txt:
      27519 = 1920 (0x0780)   27520 = 304 (0x0130)
      27521 = -123 (0xFF85)   27522 = 0xFF02
    The app labels this workgroup "Charge / Power 123 W / Week Mon", which is
    what proves the field is signed watts and not a percentage.
    """
    d = describe_schedule(1920, 304, -123, 0xFF02)
    assert d["start"] == "19:20"
    assert d["end"] == "03:04"
    assert d["enabled"] is True
    assert d["days"] == ["Mon"]
    assert d["power_w"] == -123
    assert schedule_label(1920, 304, 0xFF02) == "19:20-03:04"


def test_charge_is_negative_discharge_is_positive():
    """Sign convention: charge < 0, discharge > 0 (matches the app)."""
    charge = describe_schedule(1920, 304, -123, 0xFF02)
    discharge = describe_schedule(1920, 304, 123, 0xFF02)
    assert charge["power_w"] < 0 < discharge["power_w"]


def test_power_within_rated_power():
    """900 W must be a legal value now that the field is watts (max 980)."""
    d = describe_schedule(700, 800, 900, 0xFF7F)
    assert d["power_w"] == 900

