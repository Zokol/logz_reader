import click
from main import LogzSearch

@click.command()
@click.option('--start', '-s', required=True, type=str, help='Start time for exporting logs, in format: 2022-07-14T00:00:00.00+00:00')
@click.option('--end', '-e', required=True, type=str, help='End time for exporting logs, in format: 2022-07-15T00:00:00.00+00:00')
@click.option('--save', '-s', is_flag=True, help='Save logs to file')
@click.option('--print', '-p', is_flag=True, help='Print logs to standard output')
@click.option('--debug', '-d', is_flag=True, help='Enable debug')
@click.pass_context
def run(ctx, start, end, save, print, debug):
    search = LogzSearch(start=start, end=end, save=save, stdout=print, debug=debug)
    search.run()

if __name__ == "__main__":
    run()

