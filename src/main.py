import requests
import json
import time
import datetime
import pytz

def calc_days(start, end = None):
    timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"

    if end:
        b = datetime.datetime.strptime(end, timestamp_conversion_string)
    else:
        b = datetime.datetime.now(pytz.utc)

    a = datetime.datetime.strptime(start, timestamp_conversion_string)

    return (b - a).days

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

    print(f"Searching between: {start_time} - {end_time}")

    while convert_time(end_time) > convert_time(start_time):

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
            time.sleep(1)


if __name__ == "__main__":
    TOKEN = "6f8011f4-d20e-4ecc-9443-16376436c685"
    URL = "https://api-eu.logz.io/v1/search"
    start_time = "2022-08-01T00:00:00.00+01:00"
    end_time = "2022-08-02T00:00:00.00+01:00"

    assert calc_days(start_time, end_time) <= 2, "Logz only supports exporting logs within 2 day time window"

    URL = URL + "?dayOffset=" + str(calc_days(start_time))

    logs = export_logs(TOKEN, URL, start_time, end_time)

    timestamp_conversion_string = "%Y-%m-%dT%H:%M:%S.%f%z"
    timestamp_for_filename = "%Y-%m-%dT%H%M%S"

    str_start_time = datetime.datetime.strptime(start_time, timestamp_conversion_string).strftime(timestamp_for_filename)
    str_end_time = datetime.datetime.strptime(end_time, timestamp_conversion_string).strftime(timestamp_for_filename)
    output_filename = "logz-io_" + str_start_time + "_" + str_end_time + ".txt"
    #output_filename = "logz-io.txt"

    if len(logs) > 0:
        pretty_print(logs)
        with open(output_filename, "w") as file:
            for row in logs:
                log_data = row['_source']
                try:
                    file.writelines(f"{log_data['@timestamp']} | {log_data['syslog5424_host']} | {log_data['message']}\n")
                except KeyError:
                    pass

