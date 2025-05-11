from pathlib import Path
from pprint import pprint
import logging
from typing import List, Any, Union, Set
from dataclasses import dataclass, asdict
import csv
from datetime import datetime, timedelta
import time


timestamp_t = int

@dataclass
class Metric:
    name: str
    value: float
    # might be date or date+time
    timestamp: timestamp_t


def get_metric_files(dir: Union[str, Path], glob_pattern: str = "**/*") -> List[Path]:
    if not Path(dir).exists():
        logging.warning(f"{dir} does not exist")
        return list()

    return list(Path(dir).glob(glob_pattern))


def get_all_dates_within_daterange(start_date_t: timestamp_t, end_date_t: timestamp_t) -> List[timestamp_t]:
    """
    For specified dates interval returns list of all dates. Start and end dates are included
    """
    start_date = datetime.fromtimestamp(start_date_t)
    end_date = datetime.fromtimestamp(end_date_t)
    delta = end_date - start_date   # returns timedelta
    dates_for_interval: List[int] = list()
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        # print(day)
        dates_for_interval.append(int(day.timestamp()))

    return dates_for_interval


def metrics_list_normalize_by_missing_dates(metrics: List[Metric]) -> List[Metric]:
    """
    For passed list of metrics fill in metrics with zero values for missing dates.
    """
    metrics =  sorted(metrics, key=lambda x: x.timestamp)
    metric_0 = metrics[0]
    dates_for_metrics: Set[timestamp_t] = set(m.timestamp for m in metrics)
    all_dates_for_interval = get_all_dates_within_daterange(metrics[0].timestamp, metrics[-1].timestamp)
    if len(metrics) > len(all_dates_for_interval):
        raise ValueError(f"More metrics then all dates for interval. Consistency error. Should never get here")
    
    for d in all_dates_for_interval:
        if d not in dates_for_metrics:
            m = Metric(metric_0.name, value=0.0, timestamp=d)
            metrics.append(m)
            print(f"Add missing date with zero value {m}")

    return sorted(metrics, key=lambda x: x.timestamp)
    

def process_readiness_score_csv_file(datafile: Path) -> List[Metric]:
    if not datafile.exists():
        logging.warning(f"{datafile} does not exist")
        return list()

    timestamp_index = 0
    readiness_score_value_index = 1
    metrics: List[Metric] = list()
    with open(datafile, "r", newline="") as in_file:
        scv_reader = csv.reader(in_file, delimiter=",")

        for i, row in enumerate(scv_reader):
            # skip first row with column names
            if i == 0:
                continue

            timestamp = row[timestamp_index]
            # date format is 2023-08-08
            try:
                timestamp = int(datetime.strptime(timestamp, "%Y-%m-%d").timestamp())
            except ValueError:
                logging.warning(f"Error processing date: {row}")
                continue

            value = row[readiness_score_value_index]
            try:
                value = float(value)
            except ValueError:
                logging.warning(f"Error processing value: {row}")
                continue

            m = Metric(name="readiness_score", value=value, timestamp=timestamp)
            metrics.append(m)
            # for debug
            # print(f"{row} >> {m}")

        return metrics


def readiness_score(data_root_dir: Union[str, Path]) -> List[Metric]:
    readiness_score_files = get_metric_files(Path(data_root_dir).joinpath("Physical Activity_GoogleData"), "**/daily_readiness*.csv")
    pprint(readiness_score_files)

    readiness_score_metrics: List[Metric] = list()

    for f in readiness_score_files:
        readiness_score_metrics.extend(process_readiness_score_csv_file(f))

    # print(f"Readiness score values: {len(readiness_score_metrics)}")
    readiness_score_metrics = metrics_list_normalize_by_missing_dates(readiness_score_metrics)

    return readiness_score_metrics
