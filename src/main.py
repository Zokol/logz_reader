import requests
import json
import time
import datetime
import pytz

TOKEN = "6f8011f4-d20e-4ecc-9443-16376436c685"
URL = "https://api-eu.logz.io/v1/search"

class LogzSearch:
    def __init__(self, start, end, save=False, stdout=True, debug=False):
        self.start_time = start
        self.end_time = end
        self.logs = []
        self.save = save
        self.stdout = stdout
        self.token = TOKEN
        self.debug = debug

        assert self.calc_days(self.start_time, self.end_time) <= 2, \
            "Logz only supports exporting logs within 2 day time window"

        self.url = URL + "?dayOffset=" + str(self.calc_days(start_time))

        if self.save:
            with open(self.output_filename() + ".log", "x") as file:
                file.close()
            with open(self.output_filename() + ".json", "x") as file:
                file.writelines("[")
                file.close()

    def run(self):
        self.export_logs(self.start_time, self.end_time)
        self.close_logs()

    def calc_days(self, start, end = None):
        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"

        if end:
            b = datetime.datetime.strptime(end, timestamp_conversion_string)
        else:
            b = datetime.datetime.now(pytz.utc)

        a = datetime.datetime.strptime(start, timestamp_conversion_string)

        return (b - a).days

    def convert_time(self, timestamp):
        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        return time.mktime(datetime.datetime.strptime(timestamp, timestamp_conversion_string).timetuple())

    def output_filename(self):
        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        timestamp_for_filename = "%Y-%m-%dT%H%M%S"

        str_start_time = datetime.datetime.strptime(self.start_time, timestamp_conversion_string).strftime(
            timestamp_for_filename)
        str_end_time = datetime.datetime.strptime(self.end_time, timestamp_conversion_string).strftime(
            timestamp_for_filename)
        output_filename = "logz-io_" + str_start_time + "_" + str_end_time
        return output_filename

    def pretty_print(self, logs):
        for row in logs:
            log_data = row['_source']
            try:
                print(f"{log_data['@timestamp']} | {log_data['syslog5424_host']} | {log_data['message']}")
            except KeyError:
                pass

    def export_logs(self, start_time, end_time):

        header = {
            'Content-Type': 'application/json',
            'X-API-TOKEN': self.token
        }

        logs = []

        if self.debug: print(f"Searching between: {start_time} - {end_time}")

        while self.convert_time(end_time) > self.convert_time(start_time):

            data = {
                "query": {
                    "bool": {
                        "must": {
                            "range": {
                                "@timestamp": {
                                    "gte": start_time,
                                    "lte": end_time
                                }
                            }
                        }
                    }
                },
                "size": 10000,
                "sort": [
                    "@timestamp"
                ]
            }

            r = requests.post(url=self.url, data=json.dumps(data), headers=header)
            results = r.json()['hits']['hits']
            if len(results) == 0:
                if self.debug: print("No results found")
                return logs
            next_start_time = max(
                results,
                key=lambda row: self.convert_time(row['_source']['@timestamp'])
            )['_source']['@timestamp']
            if start_time == next_start_time:
                if self.debug: print("No newer logs found, stopping export.")
                return logs

            else:
                logs += results
                if self.save: self.save_logs(logs)
                if self.stdout: self.pretty_print(logs)
                start_time = next_start_time
                if self.debug: print(f"Next search between: {start_time} - {end_time}")
                time.sleep(1)


    def save_logs(self, logs):
        if len(logs) > 0:

            with open(self.output_filename() + ".log", "a") as file:
                for row in logs:
                    log_data = row['_source']
                    try:
                        file.writelines(
                            f"{log_data['@timestamp']} | {log_data['syslog5424_host']} | {log_data['message']}\n")
                    except KeyError:
                        pass

            with open(self.output_filename() + ".json", "a") as file:
                for row in logs:
                    try:
                        file.writelines(json.dumps(row) + ",")
                    except KeyError:
                        pass

    def close_logs(self):
        with open(self.output_filename() + ".json", "a") as file:
            file.writelines("]")


if __name__ == "__main__":
    start_time = "2022-07-02T10:00:00.00+00:00"
    end_time = "2022-07-02T10:01:00.00+00:00"

    search = LogzSearch(start=start_time, end=end_time, save=True, stdout=False, debug=True)
    search.run()


