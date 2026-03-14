# Configuration Guide

TraceLite uses a `tracelite.toml` file for configuration.

---

## Example

```toml
[tracelite]
enabled = true

[storage]
type = "sqlite"
path = "tracelite.db"

[filter]
exclude_paths = ["/static", "/favicon.ico", "/_tracelite"]
mask_keys = ["password", "token", "authorization", "secret"]

[capture]
capture_body = true
capture_sql = false

[dashboard]
path = "/_tracelite"

[slow]
threshold_ms = 1000

[view]
columns = ["timestamp", "client_ip", "method", "path", "status", "duration"]
```

---

## Sections

| Section / Key         | Type    | Default                                          | Description                                         |
|----------------------|:-------:|:------------------------------------------------:|-----------------------------------------------------|
| `[tracelite]`        |        |                                                  | Global settings                                     |
| `enabled`            | bool    | `true`                                           | Enable or disable TraceLite                         |
| `[storage]`          |        |                                                  | Storage configuration                               |
| `type`               | string  | `"sqlite"`                                       | Storage type. Currently only `sqlite` is supported  |
| `path`               | string  | `"tracelite.db"`                                 | Path to SQLite database file                        |
| `[filter]`           |        |                                                  | Filter and masking configuration                    |
| `exclude_paths`      | list    | `["/static", "/favicon.ico"]`                    | List of request paths to exclude from logging       |
| `mask_keys`          | list    | `["password", "token", "authorization", "secret"]` | List of keys to mask in headers and bodies        |
| `[capture]`          |        |                                                  | Body and SQL capture settings                       |
| `capture_body`       | bool    | `true`                                           | Capture request and response bodies                 |
| `capture_sql`        | bool    | `false`                                          | Capture SQL queries per request                     |
| `[dashboard]`        |        |                                                  | Embedded dashboard settings                         |
| `path`               | string  | `"/_tracelite"`                                  | URL path for the dashboard                          |
| `[slow]`             |        |                                                  | Slow request detection                              |
| `threshold_ms`       | int     | `1000`                                           | Duration threshold (ms) for slow request highlighting |
| `[view]`             |        |                                                  | CLI viewer configuration                            |
| `columns`            | list    | `["timestamp", "client_ip", "method", "path", "status", "duration"]` | Columns to display in CLI viewer output |

---

## Notes

- The `tracelite.toml` file should be placed in your project root directory.
- All sections and keys are optional. Default values will be used if omitted.
- It is recommended to mask sensitive keys like `password`, `token`, `authorization` when logging request/response data.
- Configuration can also be set programmatically via `TraceliteConfig`.
