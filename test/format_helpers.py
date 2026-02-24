import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math
from census_client import get_variable_label, get_variable_format, format_value

def test_get_variable_label():
    print("Testing get_variable_label...")

    label = get_variable_label("B01001_001E")
    assert label == "Total Population", f"Expected 'Total Population', got '{label}'"
    print(f"  B01001_001E -> '{label}'")

    label = get_variable_label("B01002_001E")
    assert label == "Median Age", f"Expected 'Median Age', got '{label}'"
    print(f"  B01002_001E -> '{label}'")

    unknown = get_variable_label("UNKNOWN_CODE")
    assert unknown == "UNKNOWN_CODE", f"Expected 'UNKNOWN_CODE' as fallback, got '{unknown}'"
    print(f"  UNKNOWN_CODE -> '{unknown}' (fallback to code itself)")

    print("get_variable_label: PASSED\n")

def test_get_variable_format():
    print("Testing get_variable_format...")

    fmt = get_variable_format("B01001_001E")
    assert fmt == ",", f"Expected ',', got '{fmt}'"
    print(f"  B01001_001E -> '{fmt}'")

    fmt = get_variable_format("B01002_001E")
    assert fmt == ".1f", f"Expected '.1f', got '{fmt}'"
    print(f"  B01002_001E -> '{fmt}'")

    fmt = get_variable_format("UNKNOWN_CODE")
    assert fmt == ",", f"Expected ',' as default, got '{fmt}'"
    print(f"  UNKNOWN_CODE -> '{fmt}' (default fallback)")

    print("get_variable_format: PASSED\n")

def test_format_value():
    print("Testing format_value...")

    result = format_value(1000000, "B01001_001E")
    assert result == "1,000,000", f"Expected '1,000,000', got '{result}'"
    print(f"  format_value(1000000, 'B01001_001E') -> '{result}'")

    result = format_value(38.7, "B01002_001E")
    assert result == "38.7", f"Expected '38.7', got '{result}'"
    print(f"  format_value(38.7, 'B01002_001E') -> '{result}'")

    result = format_value(float("nan"), "B01001_001E")
    assert result == "N/A", f"Expected 'N/A' for NaN, got '{result}'"
    print(f"  format_value(NaN, 'B01001_001E') -> '{result}'")

    result = format_value(None, "B01001_001E")
    assert result == "N/A", f"Expected 'N/A' for None, got '{result}'"
    print(f"  format_value(None, 'B01001_001E') -> '{result}'")

    result = format_value(0, "B01001_001E")
    assert result == "0", f"Expected '0', got '{result}'"
    print(f"  format_value(0, 'B01001_001E') -> '{result}'")

    print("format_value: PASSED\n")

if __name__ == "__main__":
    test_get_variable_label()
    test_get_variable_format()
    test_format_value()
    print("All tests passed!")
