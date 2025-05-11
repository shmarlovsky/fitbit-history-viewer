from pathlib import Path
from typing import List, Any, Union, Set
from dataclasses import dataclass, asdict
import time

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateError

from fitbit_data import Metric, readiness_score

# DATADIR = r"/mnt/d/temp/fitbit-takeout-20241219T132719Z-001/Takeout/Fitbit"
DATADIR = r"D:/Downloads/fitbit-takeout-20250509T123048Z-001/Takeout/Fitbit"


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

    with open(output_file, "w", encoding="utf-8") as outf:
        _ = outf.write(html)

    print(f"{output_file} report generated")


def main():
    start = time.perf_counter()

    readiness_score_metrics = readiness_score(DATADIR)
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
