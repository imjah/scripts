import countdown
import pytest

def test_parse_seconds_empty():
    with pytest.raises(IndexError):
        countdown.parse_seconds("")

def test_parse_seconds_no_value():
    with pytest.raises(ValueError):
        countdown.parse_seconds("s")

def test_parse_seconds_no_unit():
    assert countdown.parse_seconds("5") == 5

def test_parse_seconds_in_seconds():
    assert countdown.parse_seconds("5s") == 5

def test_parse_seconds_in_minutes():
    assert countdown.parse_seconds("5m") == 300

def test_parse_seconds_in_hours():
    assert countdown.parse_seconds("5h") == 18000
