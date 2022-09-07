# Logz.io exporter

This python application utilizes the Logz.io API to export logs between given timestamps.

Logz.io allows exporting up to 50 000 rows using the web user interface. 
Via Logz.io API "/search"-endpoint one query is limited to 10000 queries.

This tool combines the rows into single output, either to standard output or file.


# Setup
**Fetch your Logz.io token from admin-panel betfore continuing**
```
python3 -m pip install -r requirements.txt
export TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

# Usage
## Parameters
```
Usage: run.py [OPTIONS]

Options:
  -s, --start TEXT  Start time for exporting logs, in format:
                    2022-07-14T00:00:00.00+00:00  [required]
  -e, --end TEXT    End time for exporting logs, in format:
                    2022-07-15T00:00:00.00+00:00  [required]
  -s, --save        Save logs to file
  -p, --print       Print logs to standard output
  -d, --debug       Enable debug
  --help            Show this message and exit.
```

## Example
To export logs between 16.7.2022 and 17.7.2022 and save results to file;
```
.\run.py --start=2022-07-16T00:00:00.00+00:00 --end=2022-07-17T00:00:00.00+00:00 -s
```