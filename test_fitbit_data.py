from typing import List
from datetime import datetime

from fitbit_data import metrics_list_normalize_by_missing_dates, Metric

def test_metrics_list_normalize_by_missing_dates():
    pass
    metrics: List[Metric] = [
        Metric("m", 1.0, int(datetime.strptime("2025-04-01", "%Y-%m-%d").timestamp())),
        Metric("m", 2.0, int(datetime.strptime("2025-04-02", "%Y-%m-%d").timestamp())),
        Metric("m", 9.0, int(datetime.strptime("2025-04-09", "%Y-%m-%d").timestamp())),
        Metric("m", 10.0, int(datetime.strptime("2025-04-10", "%Y-%m-%d").timestamp())),
    ]

    expected: List[Metric] = [
        Metric("m", 1.0, int(datetime.strptime("2025-04-01", "%Y-%m-%d").timestamp())),
        Metric("m", 2.0, int(datetime.strptime("2025-04-02", "%Y-%m-%d").timestamp())),
        Metric("m", 0.0, int(datetime.strptime("2025-04-03", "%Y-%m-%d").timestamp())),
        Metric("m", 0.0, int(datetime.strptime("2025-04-04", "%Y-%m-%d").timestamp())),
        Metric("m", 0.0, int(datetime.strptime("2025-04-05", "%Y-%m-%d").timestamp())),
        Metric("m", 0.0, int(datetime.strptime("2025-04-06", "%Y-%m-%d").timestamp())),
        Metric("m", 0.0, int(datetime.strptime("2025-04-07", "%Y-%m-%d").timestamp())),
        Metric("m", 0.0, int(datetime.strptime("2025-04-08", "%Y-%m-%d").timestamp())),
        Metric("m", 9.0, int(datetime.strptime("2025-04-09", "%Y-%m-%d").timestamp())),
        Metric("m", 10.0, int(datetime.strptime("2025-04-10", "%Y-%m-%d").timestamp())),
    ]

    result = metrics_list_normalize_by_missing_dates(metrics=metrics)
    assert result == expected