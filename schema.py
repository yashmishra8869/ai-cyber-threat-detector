from __future__ import annotations

import re
from typing import Iterable, List

FEATURE_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
]

TARGET_COLUMN = "attack_name"
DIFFICULTY_COLUMN = "difficulty"
EXPECTED_COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN, DIFFICULTY_COLUMN]

CATEGORICAL_FEATURES = ["protocol_type", "service", "flag"]
NUMERIC_FEATURES = [column for column in FEATURE_COLUMNS if column not in CATEGORICAL_FEATURES]

VALID_PROTOCOL_TYPES = {"tcp", "udp", "icmp"}
VALID_FLAGS = {
    "SF", "S0", "REJ", "RSTR", "RSTO", "SH", "S1", "S2", "S3", "OTH",
    "RSTOS0", "OOTH", "S4", "RSTRH", "SHR"
}
VALID_SERVICES = {
    "http", "ftp", "smtp", "domain", "auth", "private", "ftp_data", "echo",
    "telnet", "time", "gopher", "finger", "imap4", "domain_u", "tftp_u",
    "csnet_ns", "uucp_path", "name", "netbios_ns", "netbios_ssn", "netbios_dgm",
    "sql_net", "vmnet", "link", "sunrpc", "exec", "courier", "discard",
    "systat", "daytime", "netstat", "pop_3", "nnsp", "http_443", "login",
    "efs", "whois", "shell", "kshell", "hostnames", "iso_tsap", "klogin",
    "supdup", "bgp", "ldap", "urh_i", "X11", "urp_i", "icmp", "eco_i",
    "ecr_i", "red_i", "other", "aol", "IRC", "Z39_50", "ctf", "harvest"
}

KNOWN_ATTACK_LABELS = {
    "normal",
    "back",
    "buffer_overflow",
    "ftp_write",
    "guess_passwd",
    "imap",
    "ipsweep",
    "land",
    "loadmodule",
    "multihop",
    "neptune",
    "nmap",
    "perl",
    "phf",
    "pod",
    "portsweep",
    "rootkit",
    "satan",
    "smurf",
    "spy",
    "teardrop",
    "warezclient",
    "warezmaster",
    "xlock",
    "xsnoop",
    "worm",
    "snmpgetattack",
    "httptunnel",
    "sendmail",
    "named",
    "ps",
    "saint",
    "mscan",
    "apache2",
    "processtable",
    "sqlattack",
    "udpstorm",
    "mailbomb",
    "ipsec",
    "smb",
    "rsh",
    "distcc",
    "ncftp",
    "syslog",
    "wuwei",
    "snmpguess",
    "xterm",
    "ppmacro",
    "tftp",
}


def _is_valid_service_value(value: str) -> bool:
    if value is None:
        return False
    value = str(value).strip()
    if value == "":
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", value))


def validate_expected_schema(df) -> None:
    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_numeric_values(df, numeric_columns: Iterable[str] | None = None) -> None:
    columns = list(numeric_columns) if numeric_columns is not None else NUMERIC_FEATURES
    for column in columns:
        if column not in df.columns:
            raise ValueError(f"Numeric validation failed: missing column '{column}'")
        values = pd.to_numeric(df[column], errors="raise")
        if values.isnull().any():
            raise ValueError(f"Numeric validation failed: column '{column}' contains missing values")
        if not values.map(float).apply(lambda value: value == value and value not in (float("inf"), float("-inf"))).all():
            raise ValueError(f"Numeric validation failed: column '{column}' contains non-finite values")


def convert_target_to_binary(labels) -> List[int]:
    binary_values = []
    for label in labels:
        value = str(label).strip().lower()
        if value == "normal":
            binary_values.append(0)
        elif value in KNOWN_ATTACK_LABELS:
            binary_values.append(1)
        else:
            raise ValueError(
                f"Unexpected target label '{label}'. Supported labels include 'normal' and known NSL-KDD attack names."
            )
    return binary_values


def validate_categorical_values(df, categorical_columns: Iterable[str] | None = None) -> None:
    columns = list(categorical_columns) if categorical_columns is not None else CATEGORICAL_FEATURES
    for column in columns:
        if column not in df.columns:
            raise ValueError(f"Categorical validation failed: missing column '{column}'")

        values = df[column].astype(str).str.strip()
        if values.eq("").any():
            raise ValueError(f"Categorical validation failed: column '{column}' contains empty values")

        if column == "protocol_type":
            invalid = sorted(set(values) - VALID_PROTOCOL_TYPES)
            if invalid:
                raise ValueError(f"Invalid protocol_type values found: {invalid[:5]}")
        elif column == "flag":
            invalid = sorted(set(values) - VALID_FLAGS)
            if invalid:
                raise ValueError(f"Invalid flag values found: {invalid[:5]}")
        elif column == "service":
            invalid = sorted({str(value) for value in values.tolist() if not _is_valid_service_value(value)})
            if invalid:
                raise ValueError(f"Invalid service values found: {invalid[:5]}")


try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None
