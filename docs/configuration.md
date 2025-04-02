# Configuration Guide

Tracelite uses a `tracelite.toml` file for configuration.

---

## Example

```toml
[tracelite]
enabled = true

[storage]
type = "sqlite"
path = "tracelite.db"

[filter]
exclude_paths = ["/static", "/favicon.ico"]
mask_keys = ["password", "token"]

[view]
columns = ["timestamp", "client_ip", "method", "path", "status", "duration"]
```

---

## Sections

| Section / Key         | Type    | Default                                          | Description                                         |
|----------------------|:-------:|:------------------------------------------------:|-----------------------------------------------------|
| `[tracelite]`        |        |                                                  | Global settings                                     |
| `enabled`            | bool    | `true`                                           | Enable or disable Tracelite                         |
| `[storage]`          |        |                                                  | Storage configuration                               |
| `type`               | string  | `"sqlite"`                                       | Storage type. Currently only `sqlite` is supported  |
| `path`               | string  | `"tracelite.db"`                                 | Path to SQLite database file                        |
| `[filter]`           |        |                                                  | Filter and masking configuration                    |
| `exclude_paths`      | list    | `[]`                                             | List of request paths to exclude from logging       |
| `mask_keys`          | list    | `[]`                                             | List of keys to mask in request/response headers or body |
| `[view]`             |        |                                                  | CLI viewer configuration                            |
| `columns`            | list    | `["timestamp", "client_ip", "method", "path", "status", "duration"]` | Columns to display in CLI viewer output |

---

## Notes

- The `tracelite.toml` file should be placed in your project root directory.
- All sections and keys are optional. Default values will be used if omitted.
- It is recommended to mask sensitive keys like `password`, `token`, `authorization` when logging request/response data.