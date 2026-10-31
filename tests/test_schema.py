import pandas as pd

from schema import convert_target_to_binary, validate_categorical_values, validate_numeric_values


def test_convert_target_to_binary_normal_and_attack():
    labels = ["normal", "back", "ipsweep", "normal"]
    assert convert_target_to_binary(labels) == [0, 1, 1, 0]


def test_convert_target_to_binary_raises_for_unknown_label():
    try:
        convert_target_to_binary(["unexpected_label"])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_validate_numeric_values_works():
    df = pd.DataFrame({
        "duration": [0.0, 1.5],
        "src_bytes": [10, 20],
        "dst_bytes": [30, 40],
    })
    validate_numeric_values(df, ["duration", "src_bytes", "dst_bytes"])


def test_validate_categorical_values_works():
    df = pd.DataFrame({
        "protocol_type": ["tcp", "udp"],
        "service": ["http", "smtp"],
        "flag": ["SF", "REJ"],
    })
    validate_categorical_values(df)


def test_validate_categorical_values_accepts_legitimate_nsl_kdd_services():
    df = pd.DataFrame({
        "protocol_type": ["tcp", "tcp", "udp"],
        "service": ["IRC", "Z39_50", "aol"],
        "flag": ["SF", "REJ", "S0"],
    })
    validate_categorical_values(df)


def test_validate_categorical_values_rejects_empty_service_value():
    df = pd.DataFrame({
        "protocol_type": ["tcp"],
        "service": [""],
        "flag": ["SF"],
    })
    try:
        validate_categorical_values(df)
        assert False, "Should have raised ValueError for empty service value"
    except ValueError:
        pass
