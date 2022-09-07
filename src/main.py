import requests
import json
import time
import datetime
import pytz
from dotenv import load_dotenv
import os


class LogzSearch:
    def __init__(self, start, end, save=False, stdout=True, debug=False, filters=None, limit=None):
        load_dotenv()

        self.start_time = start
        self.end_time = end
        self.logs = []
        self.save = save
        self.stdout = stdout
        self.token = os.environ.get("TOKEN")
        self.debug = debug

        # Logrow filter
        # Example: {"syslog5452_host": "ubuntu"}, this filters out all hosts that do not have "ubuntu" in the hostname
        self.filters = filters
        self.limit = limit

        # Logz.io limits one query between two consecutive days
        # Generate list of timestamps and URLs to allow searching between longer periods of time
        self.queries = []
        temp_start = self.start_time

        # If query is for longer than two days, split queries into 24 hour blocks
        while self.day_difference(temp_start, self.end_time) > 2:
            temp_end = temp_start + datetime.timedelta(days=1)
            self.queries.append({
                "url": os.environ.get("URL") + "?dayOffset=" + str(self.offset_days(temp_start)),
                "start_time": temp_start,
                "end_time": temp_end
            })
            temp_start = temp_end

        # Finally, last (or only) query is for the remaining period of time, limited to 2 days
        self.queries.append({
            "url": os.environ.get("URL") + "?dayOffset=" + str(self.offset_days(temp_start)),
            "start_time": temp_start,
            "end_time": self.end_time
        })


        if self.save:
            with open(self.output_filename() + ".log", "x") as file:
                file.close()
            with open(self.output_filename() + ".json", "x") as file:
                file.writelines("[")
                file.close()

    def run(self):
        """
        Main function for running the Logz.io export
        """
        for query in self.queries:
            self.export_logs(query["url"], query["start_time"], query["end_time"])
        self.close_logs()


    def day_difference(self, start, end):
        """
        It takes two timestamps in the format of "YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM" and returns the number of days between
        them

        :param start: The start date of the time period you want to analyze
        :param end: The end date of the time period you want to analyze
        :return: The difference in days between the start and end dates.
        """
        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"

        b = datetime.datetime.strptime(end, timestamp_conversion_string)
        a = datetime.datetime.strptime(start, timestamp_conversion_string)

        return (b - a).days

    def offset_days(self, start):
        """
        It takes a timestamp in the format of `YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM` and returns the number of days between the
        timestamp and the current time

        :param start: The start time of the event
        :return: The number of days between the current time and the start time.
        """
        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"

        b = datetime.datetime.now(pytz.utc)
        a = datetime.datetime.strptime(start, timestamp_conversion_string)

        return (b - a).days

    def convert_logz_timestamp_to_unix(self, timestamp):
        """
        It takes a timestamp logz.io timestamp and converts it to a Unix timestamp

        :param timestamp: The timestamp to convert
        :return: The time in seconds since the epoch.
        """
        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        logz_timestamp = datetime.datetime.strptime(timestamp, timestamp_conversion_string)
        return logz_timestamp.timestamp()

    def convert_unix_to_logz_timestamp(self, unix_timestamp):
        """
        Given a unix timestamp, convert it to a logz.io timestamp

        :param timestamp: The timestamp of the event
        :return: The time in seconds since the epoch.
        """

        timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        unix_datetime = datetime.datetime.utcfromtimestamp(unix_timestamp).replace(tzinfo=pytz.UTC)
        return unix_datetime.strftime(timestamp_conversion_string)

    def output_filename(self):
        """
        It takes the query timestamps and generates a filename for exported data.

        :return: The output_filename method returns a string that is the name of the file that will be created.
        """
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

    def export_logs(self, url, start_time, end_time):

        header = {
            'Content-Type': 'application/json',
            'X-API-TOKEN': self.token
        }

        logs = []

        query_size = 10000

        if self.debug: print(f"Searching between: {start_time} - {end_time}")

        while self.convert_logz_timestamp_to_unix(end_time) > self.convert_logz_timestamp_to_unix(start_time):

            if self.limit:
                if len(self.logs) >= self.limit:
                    if self.debug: print("Export limit reached")
                    return logs
                if query_size + len(self.logs) > self.limit:
                    query_size = self.limit - len(self.logs)

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

            r = requests.post(url=url, data=json.dumps(data), headers=header)
            results = r.json()['hits']['hits']
            results = self.filter(results)

            if len(results) == 0:
                if self.debug: print("No results found")
                return logs

            next_start_time = max(
                results,
                key=lambda row: self.convert_logz_timestamp_to_unix(row['_source']['@timestamp'])
            )['_source']['@timestamp']

            # Stop fetching logs if we do not get newer logs
            if start_time == next_start_time:
                if self.debug: print("No newer logs found, stopping export.")
                return logs

            else:
                logs += results
                if self.save: self.save_logs(results)
                if self.stdout: self.pretty_print(results)
                start_time = next_start_time
                if self.debug: print(f"Next search between: {start_time} - {end_time}")

    def save_logs(self, logs):
        if len(logs) > 0:

            with open(self.output_filename() + ".log", "a") as file:
                for row in logs:
                    log_data = row['_source']
                    try:
                        file.writelines(
                            f"{log_data['@timestamp']} |"
                            f" {log_data['syslog5424_host']} |"
                            f" {log_data['message']}\n"
                        )
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

    def filter(self, input):
        """
        It takes a list of log rows and filters out the rows that do not contain the search parameters

        :param input: The input data to be filtered
        :return: Filtered data
        """
        output = []
        for row in input:
            log_data = row['_source']
            for filter in self.filters.keys():
                if filter in log_data:
                    if self.filter[filter] not in log_data[filter]:
                        output.append(row)
        return output




if __name__ == "__main__":
    start_time = "2022-07-14T00:00:00.00+00:00"
    end_time = "2022-07-15T00:00:00.00+00:00"

    search = LogzSearch(start=start_time, end=end_time, save=True, stdout=False, debug=True)
    search.run()
