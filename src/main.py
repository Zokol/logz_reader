import requests
import json
import time
import datetime

def convert_time(timestamp):
    timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"
    return time.mktime(datetime.datetime.strptime(timestamp, timestamp_conversion_string).timetuple())

def pretty_print(logs):
    for row in logs:
        log_data = row['_source']
        try:
            print(f"{log_data['@timestamp']} | {log_data['syslog5424_host']} | {log_data['message']}")
        except KeyError:
            pass

def export_logs(token, url, start_time, end_time):

    header = {
        'Content-Type': 'application/json',
        'X-API-TOKEN': token
    }

    logs = []

    while convert_time(end_time) > convert_time(start_time):

        print(f"Next search between: {start_time} - {end_time}")

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
            "size": 1000
        }

        r = requests.post(url=url, data=json.dumps(data), headers=header)
        results = r.json()['hits']['hits']
        if len(results) == 0:
            print("No results found")
            return logs
        next_start_time = max(results, key=lambda row: convert_time(row['_source']['@timestamp']))['_source']['@timestamp']
        if start_time == next_start_time:
            print("No newer logs found, stopping export.")
            return logs

        else:
            logs += results
            start_time = next_start_time
            print(f"Next search between: {start_time} - {end_time}")

if __name__ == "__main__":
    TOKEN = "6f8011f4-d20e-4ecc-9443-16376436c685"
    URL = "https://api-eu.logz.io/v1/search"
    start_time = "2022-07-07T00:00:00.00+01:00"
    end_time = "2022-07-10T00:00:00.00+01:00"
    logs = export_logs(TOKEN, URL, start_time, end_time)

    if len(logs) > 0:
        pretty_print(logs)
        with open("logz-io_" + start_time + "_" + end_time + ".txt", "w") as file:
            file.writelines(logs)
