import logging
import subprocess
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage

app = typer.Typer()

# Load configuration
config = load_config()
storage = SQLiteStorage(db_path=config.db_path)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def parse_filters(filters: list[str]) -> dict:
    result = {}
    for f in filters:
        if "=" in f:
            key, value = f.split("=", 1)
            result[key.strip()] = value.strip()
    return result


@app.command()
def view(
    since: int = 3600,
    columns: Optional[str] = typer.Option(
        None,
        "--columns",
        "-c",
        help="Columns to display (comma-separated), e.g. 'timestamp,client_ip,path'",
    ),
    filter: Optional[list[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter conditions (multiple allowed), e.g. --filter 'status=500'",
    ),
):
    """View logs from the last N seconds with optional filters."""
    filters = parse_filters(filter) if filter else {}
    logs = storage.fetch_recent(since_seconds=since, filters=filters)
    if not logs:
        logging.info("No logs found.")
        return

    # Columns setting
    default_columns = ["timestamp", "client_ip", "method", "path", "status", "duration"]
    selected_columns = (
        [col.strip() for col in columns.split(",")] if columns else default_columns
    )

    # Column name mapping
    header_map = {
        "timestamp": "Timestamp",
        "client_ip": "Client IP",
        "method": "Method",
        "path": "Path",
        "status": "Status",
        "duration": "Duration (ms)",
        "headers": "Headers",
        "body": "Body",
        "response": "Response",
    }

    # Table
    table = Table(show_header=True, header_style="bold magenta")
    for col in selected_columns:
        table.add_column(
            header_map.get(col, col), justify="right" if col == "duration" else "left"
        )

    # Row mapping
    for row in logs:
        row_dict = {
            "timestamp": row[1],
            "method": row[2],
            "path": row[3],
            "status": str(row[4]),
            "client_ip": row[5],
            "headers": row[7] or "",
            "body": row[8] or "",
            "response": row[9] or "",
            "duration": (
                f"{float(row[11]):.2f}" if isinstance(row[11], (float, int)) else ""
            ),
        }
        table.add_row(*[row_dict.get(col, "") for col in selected_columns])

    console = Console()
    console.print(table)


@app.command()
def view_ui() -> None:
    """Launch Streamlit UI for viewing logs."""
    subprocess.run(["streamlit", "run", "src/tracelite/ui/viewer.py"])


@app.command()
def export(
    format: str = typer.Option(
        "json", "--format", "-f", help="Export format: json, csv"
    ),
    since: int = typer.Option(3600, "--since", help="Export logs since N seconds ago"),
    filter: Optional[list[str]] = typer.Option(
        None,
        "--filter",
        "-F",
        help="Filter conditions (multiple allowed), e.g. --filter 'status=500'",
    ),
):
    """Export logs to given format."""
    filters = parse_filters(filter) if filter else {}
    logs = storage.fetch_recent(since_seconds=since, filters=filters)
    if not logs:
        logging.info("No logs found.")
        return

    columns = ["timestamp", "client_ip", "method", "path", "status", "duration"]

    if format == "json":
        from rich import print_json

        output = [
            {
                "timestamp": row[1],
                "client_ip": row[5],
                "method": row[2],
                "path": row[3],
                "status": row[4],
                "duration": row[11],
            }
            for row in logs
        ]
        print_json(data=output)
    elif format == "csv":
        import csv
        import sys

        writer = csv.writer(sys.stdout)
        writer.writerow(columns)
        for row in logs:
            writer.writerow([row[1], row[5], row[2], row[3], row[4], row[11]])
    else:
        logging.error(f"Unsupported format: {format}")


def cli():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
