from pathlib import Path
from pprint import pprint
import logging
from typing import List, Any
from dataclasses import dataclass, asdict
import csv
from datetime import datetime
import time

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateError

DATADIR = r"/mnt/d/temp/fitbit-takeout-20241219T132719Z-001/Takeout/Fitbit"


@dataclass
class Metric:
    name: str
    value: float
    # might be date or date+time
    timestamp: int


def get_metric_files(dir: str | Path, glob_pattern: str = "**/*") -> List[Path]:
    if not Path(dir).exists():
        logging.warning(f"{dir} does not exist")
        return list()

    return list(Path(dir).glob(glob_pattern))


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


def readiness_score() -> List[Metric]:
    readiness_score_files = get_metric_files(Path(DATADIR).joinpath("Daily Readiness"), "**/Daily Readiness Score*.csv")
    pprint(readiness_score_files)

    readiness_score_metrics: List[Metric] = list()

    for f in readiness_score_files:
        readiness_score_metrics.extend(process_readiness_score_csv_file(f))

    # print(f"Readiness score values: {len(readiness_score_metrics)}")
    # sort by date
    return sorted(readiness_score_metrics, key=lambda x: x.timestamp)


def render_report(readiness_score_metrics: List[Metric], output_file: str = "dashboard.html"):
    dir_for_current_file = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(str(dir_for_current_file)))
    template = env.get_template("report_template.html")

    context: dict[str, Any] = dict()
    context["dailyReadinessData"] = list(asdict(m) for m in readiness_score_metrics)

    try:
        html = template.render(context=context)
    except TemplateError as err:
        print(f"Failed to generate report: {err}")
        return

    with open(output_file, "w") as outf:
        _ = outf.write(html)

    print(f"{output_file} report generated")


def main():
    start = time.perf_counter()

    readiness_score_metrics = readiness_score()
    render_report(readiness_score_metrics=readiness_score_metrics)

    end = time.perf_counter()
    print(f"\nProcessing time: {round(end-start, 2)}")

    # readiness score for each day
    # sleep score for each day
    # later: more sleep metrics
    # resting heartrate for each day, where to get it from?
    # highlight days with traninigs
    # amount of steps for each day


if __name__ == "__main__":
    main()
