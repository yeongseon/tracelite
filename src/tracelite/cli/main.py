import typer
import logging
from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage

app = typer.Typer()

# Load configuration from file
config = load_config()

# Initialize storage based on config
db_path = config.db_path
storage = SQLiteStorage(db_path=db_path)

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

@app.command()
def view(since: int = 3600):
    """View logs from the last N seconds."""
    logs = storage.fetch_recent(since_seconds=since)
    if not logs:
        logging.info("No logs found.")
        return

    import rich
    from rich.table import Table
    from rich.console import Console

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Timestamp")
    table.add_column("Method")
    table.add_column("Path")
    table.add_column("Status")
    table.add_column("Duration (ms)", justify="right")

    for row in logs:
        timestamp, method, path, status_code, *_ , duration_ms = row
        table.add_row(timestamp, method, path, str(status_code), f"{duration_ms:.2f}")

    console = Console()
    console.print(table)

@app.command()
def export(format: str = "json"):
    """Export logs to given format."""
    try:
        output = storage.export(format)
        from rich import print_json
        if format == "json":
            print_json(output)
        else:
            print(output)
    except Exception as e:
        logging.error(f"Export failed: {e}")
        
if __name__ == "__main__":
    app()