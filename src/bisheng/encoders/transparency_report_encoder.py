import json
import os
from datetime import datetime

from bisheng.encoders.base_encoder import BaseEncoder


class TransparencyReportEncoder(BaseEncoder):

    def __init__(self, report_dir: str):
        self.report_dir = report_dir

        if not os.path.isdir(self.report_dir):
            raise NotADirectoryError(f"Not a directory: {self.report_dir}")

    def encode(self, **input_data):
        results = input_data["results"]
        context = str(input_data["context"])
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.report_dir}/transparency_{timestamp_str}.json"
        context = str.replace(context, "\n", "") or None

        with (open(filename, "w") as f):
            f.write("{\n")
            f.write("\t\"context\": \"" + str(context) + "\",\n")
            f.write("\t\"results\": ")
            records = []
            record = {}
            for prompt, response in results.items():
                record["prompt"] = prompt.to_json()
                record["response"] = response.to_json()
                records.append(record)
            f.write(json.dumps(records, indent=4))
            f.write("}")
