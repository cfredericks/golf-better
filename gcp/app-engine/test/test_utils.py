import utils
import pytest

from datetime import date, datetime

def test_json_serial_date():
    d = date(2024, 1, 1)
    assert utils.json_serial(d) == "2024-01-01"

def test_json_serial_datetime():
    dt = datetime(2024, 1, 1)
    assert utils.json_serial(dt) == "2024-01-01T00:00:00"

def test_json_serial_int():
    with pytest.raises(TypeError):
        utils.json_serial(5)
