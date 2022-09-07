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
export URL=https://api-eu.logz.io/v1/search
```

# Usage
## Parameters
```
run.py --help
Usage: run.py [OPTIONS]

Options:
  -s, --start TEXT             Start time for exporting logs, in format:
                               2022-07-14T00:00:00.00+00:00  [required]
  -e, --end TEXT               End time for exporting logs, in format:
                               2022-07-15T00:00:00.00+00:00  [required]
  -f, --file                   Save logs to file
  -p, --print                  Print logs to standard output
  -v, --verbose                Enable verbose output
  -l, --limit INTEGER          Limit number of results to defined number
  -f, --filter <TEXT TEXT>...  Only return results where given substring is in
                               determined column. Example to only show log-
                               rows from hosts with hostname that contains the
                               string 'ubuntu': -f syslog5452_host ubuntu
  --help                       Show this message and exit.
```

## Examples

### Date range
* Export logs between 16.07.2022 and 17.07.2022 (-s and -e)
* Save results to file (-f)
```
.\run.py -s 2022-07-16T00:00:00.00+00:00 -e 2022-07-17T00:00:00.00+00:00 -f
```

### Print to screen
* Export logs between 16.07.2022 and 17.07.2022 (-s and -e)
* Print results instead of saving them on disk (-p)
```
.\run.py -s 2022-07-16T00:00:00.00+00:00 -e 2022-07-17T00:00:00.00+00:00 -p
```

### Filter by host
* Export all logs between 01.09.2022 and 15.09.2022 (-s and -e)
* Print results (-p)
* Only show logs from 'edgerouter'-host (-f)
```
.\run.py -s 2022-09-01T00:00:00.00+00:00 -e 2022-09-15T00:00:00.00+00:00 -p -f syslog5452_host edgerouter
```

### Filter by multiple hosts
* Export all logs between 01.09.2022 and 15.09.2022 (-s and -e)
* Print results (-p)
* Only show logs from 'firewall1' and 'game_dev5' (multiple -f parameters)
```
.\run.py -s 2022-09-01T00:00:00.00+00:00 -e 2022-09-15T00:00:00.00+00:00 -p -f syslog5452_host firewall1 -f syslog5452_host game_dev5
```

### Limit results
* Export logs between 01.09.2022 10AM and 01.09.2022 11AM (-s and -e)
* Print results (-p)
* Only show logs from 'firewall1' and 'game_dev5' (multiple -f parameters)
* Limit number of exported rows to 100 (-l)
```
.\run.py -s 2022-09-01T10:00:00.00+00:00 -e 2022-09-01T11:00:00.00+00:00 -p -f syslog5452_host firewall1 -f syslog5452_host game_dev5 -l 100
```