import streamlit as st
import pandas as pd
from typing import List, Tuple, Any

from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.core.config import TraceliteConfig, load_config


def load_logs(db_path: str) -> List[Tuple[Any, ...]]:
    """Load recent logs from SQLite database."""
    storage = SQLiteStorage(db_path)
    logs = storage.fetch_recent()
    return logs


def main() -> None:
    """Streamlit log viewer."""
    st.title("📄 Tracelite Request/Response Logs")

    config: TraceliteConfig = load_config()
    logs: List[Tuple[Any, ...]] = load_logs(config.db_path)

    if not logs:
        st.info("No logs found.")
        return

    df: pd.DataFrame = pd.DataFrame(
        logs,
        columns=[
            "timestamp",
            "method",
            "path",
            "status_code",
            "client_ip",
            "user_agent",
            "request_headers",
            "request_body",
            "response_headers",
            "response_body",
            "duration_ms",
        ],
    )
    st.dataframe(df)


if __name__ == "__main__":
    main()
