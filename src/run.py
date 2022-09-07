import click
from main import LogzSearch

@click.command()
@click.option('--start', '-s', required=True, type=str, help='Start time for exporting logs, in format: 2022-07-14T00:00:00.00+00:00')
@click.option('--end', '-e', required=True, type=str, help='End time for exporting logs, in format: 2022-07-15T00:00:00.00+00:00')
@click.option('--file', '-f', is_flag=True, help='Save logs to file')
@click.option('--print', '-p', is_flag=True, help='Print logs to standard output')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--limit', '-l', type=int, help='Limit number of results to defined number')
@click.option('--filter', '-f', nargs=2, type=click.Tuple([str, str]), multiple=True, default=[None, None], help="Only return results where given substring is in determined column. Example to only show log-rows from hosts with hostname that contains the string 'ubuntu': -f syslog5452_host ubuntu")
@click.pass_context
def run(ctx, start, end, file, print, verbose, limit, filter):
    filters = []
    for f in filter:
        if f[0] is not None:
            filters.append({"column":f[0], "value":f[1]})
    search = LogzSearch(start=start, end=end, save=file, stdout=print, debug=verbose, limit=limit, filters=filters)
    search.run()

if __name__ == "__main__":
    run()

