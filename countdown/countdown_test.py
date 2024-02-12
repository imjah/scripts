import countdown
import pytest

def test_parse_time_empty():
    with pytest.raises(IndexError):
        countdown.parse_time("")

def test_parse_time_no_value():
    with pytest.raises(ValueError):
        countdown.parse_time("s")

def test_parse_time_no_unit():
    assert countdown.parse_time("5") == 5

def test_parse_time_in_seconds():
    assert countdown.parse_time("5s") == 5

def test_parse_time_in_minutes():
    assert countdown.parse_time("5m") == 300

def test_parse_time_in_hours():
    assert countdown.parse_time("5h") == 18000
