from datetime import timedelta, datetime as dt
import ttv

def test_dt_one_hour_before_now():
    time = (dt.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    assert ttv.td(time) == '1h'

def test_dt_one_hour_after_now():
    time = (dt.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    assert ttv.td(time) == '-1h'

def test_dt_one_minute_before_now():
    time = (dt.utcnow() - timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    assert ttv.td(time) == '1m'

def test_dt_one_minute_after_now():
    time = (dt.utcnow() + timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    assert ttv.td(time) == '-1m'

def test_dt_one_second_before_now():
    time = (dt.utcnow() - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    assert ttv.td(time) in ['1s', '2s']

def test_dt_one_second_after_now():
    time = (dt.utcnow() + timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    assert ttv.td(time) in ['-1s', '0s']
