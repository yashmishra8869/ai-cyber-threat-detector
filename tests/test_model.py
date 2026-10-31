from pathlib import Path

import pandas as pd

from train_model import build_pipeline, train_pipeline_from_dataframe
from schema import FEATURE_COLUMNS, TARGET_COLUMN


def test_pipeline_builds():
    pipeline = build_pipeline()
    assert pipeline is not None
    assert hasattr(pipeline, "fit")


def test_train_pipeline_from_dataframe_works_on_sample_data():
    data = {
        "duration": [0, 1, 2, 3, 4, 5],
        "protocol_type": ["tcp", "udp", "icmp", "tcp", "udp", "icmp"],
        "service": ["http", "smtp", "ftp", "http", "smtp", "ftp"],
        "flag": ["SF", "REJ", "SF", "SF", "REJ", "SF"],
        "src_bytes": [10, 20, 30, 40, 50, 60],
        "dst_bytes": [5, 6, 7, 8, 9, 10],
        "land": [0, 0, 0, 0, 0, 0],
        "wrong_fragment": [0, 0, 0, 0, 0, 0],
        "urgent": [0, 0, 0, 0, 0, 0],
        "hot": [0, 0, 0, 0, 0, 0],
        "num_failed_logins": [0, 0, 0, 0, 0, 0],
        "logged_in": [1, 1, 0, 1, 0, 1],
        "num_compromised": [0, 1, 0, 1, 0, 0],
        "root_shell": [0, 0, 0, 0, 0, 0],
        "su_attempted": [0, 0, 0, 0, 0, 0],
        "num_root": [0, 1, 0, 1, 0, 0],
        "num_file_creations": [0, 0, 0, 0, 0, 0],
        "num_shells": [0, 0, 0, 0, 0, 0],
        "num_access_files": [0, 0, 0, 0, 0, 0],
        "num_outbound_cmds": [0, 0, 0, 0, 0, 0],
        "is_host_login": [0, 0, 0, 0, 0, 0],
        "is_guest_login": [0, 0, 0, 0, 0, 0],
        "count": [1, 2, 3, 4, 5, 6],
        "srv_count": [1, 2, 3, 4, 5, 6],
        "serror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "srv_serror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "rerror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "srv_rerror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "same_srv_rate": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "diff_srv_rate": [0.0, 0.1, 0.2, 0.1, 0.2, 0.3],
        "srv_diff_host_rate": [0.0, 0.0, 0.1, 0.1, 0.2, 0.2],
        "dst_host_count": [100, 80, 60, 40, 20, 10],
        "dst_host_srv_count": [50, 60, 70, 80, 90, 100],
        "dst_host_same_srv_rate": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5],
        "dst_host_diff_srv_rate": [0.0, 0.1, 0.2, 0.3, 0.2, 0.1],
        "dst_host_same_src_port_rate": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        "dst_host_srv_diff_host_rate": [0.0, 0.1, 0.2, 0.3, 0.2, 0.1],
        "dst_host_serror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "dst_host_srv_serror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "dst_host_rerror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "dst_host_srv_rerror_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "attack_name": ["normal", "normal", "back", "normal", "satan", "normal"],
        "difficulty": [0, 0, 1, 0, 2, 0],
    }

    df = pd.DataFrame(data)
    pipeline, metrics = train_pipeline_from_dataframe(df)
    assert pipeline is not None
    assert set(metrics).issuperset({"accuracy", "precision", "recall", "f1_score", "confusion_matrix"})
