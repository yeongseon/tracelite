# tracelite Development Roadmap

This roadmap outlines the planned feature development and versioning strategy of tracelite, aiming to provide a lightweight, developer-friendly CLI logging tool for testing and debugging.

---

## 🎯 Versioning Strategy

tracelite will gradually evolve through `0.x` versions to build core features.  
Once all planned features are complete and stable, **v1.0.0** will be officially released.

---

## ✅ Milestones & Features

### v0.4.x - Foundation & CLI Usability (Current)
> Initial foundation & basic CLI enhancements

- [x] Basic `view` command implementation
- [x] Add `--columns` option to control output fields
- [ ] Improve `--help` descriptions and CLI UX
- [ ] Update README with CLI usage examples
- [ ] Add `CHANGELOG.md` and maintain version history
- [ ] Add basic input validation and friendly error messages

---

### v0.5.x - Essential CLI Features (MVP)
> Provide essential CLI functionality for developer testing

- [ ] Add `--search` option to filter logs by keyword
- [ ] Add `--level` option to filter logs by log level
- [ ] Add `--follow` option for real-time log tailing
- [ ] Improve colorized and formatted log output
- [ ] Add simple stats summary in `view` command (count, error ratio)
- [ ] Add time range filter option (`--after` / `--before`)

---

### v0.6.x - Advanced Query & Export
> Make tracelite more powerful for querying and exporting logs

- [ ] Support SQL-like query options: `WHERE`, `ORDER BY`, `LIMIT`
- [ ] Add wildcard and regex search option
- [ ] Add `export` command with filtering options
- [ ] Support output formats: JSON, CSV, NDJSON
- [ ] Add configuration file support (`$HOME/.tracelite/config.toml`)
- [ ] Add option to anonymize sensitive fields when exporting

---

### v0.7.x - Log Management Features
> Enable persistent log storage and management

- [ ] Add log file automatic storage option
- [ ] Implement log rotation (size-based, date-based)
- [ ] Add log retention policy configuration
- [ ] Add option to compress old log files
- [ ] Provide log storage directory configuration
- [ ] Add `clear` command to delete old logs

---

### v0.8.x - Interactive Mode & Stats
> Provide real-time monitoring and log analysis

- [ ] Add `stats` command (total requests, error ratio, avg duration, unique paths)
- [ ] Add `monitor` command with interactive TUI dashboard
- [ ] Implement session-based log separation and management
- [ ] Add `session list` and `session delete` commands
- [ ] Provide real-time alerts in monitor mode (e.g. too many errors)
- [ ] Add option to highlight matching search terms in monitor mode

---

### v0.9.x - External Integration & Extensibility
> Connect tracelite to external systems and provide extensibility

- [ ] Add Webhook integration (Slack, Discord) for alerts
- [ ] Introduce plugin architecture for log post-processing
- [ ] Provide Python API for programmatic log access
- [ ] Add ability to load user-defined post-processing plugins
- [ ] Add notification throttle setting to avoid spamming
- [ ] Add dry-run mode for plugin testing

---

## 🚀 v1.0.0 - Stable Release
> First stable release with complete feature set

- [ ] Complete documentation & usage examples
- [ ] Ensure test coverage exceeds 80%
- [ ] Add automated release workflow (GitHub Actions → PyPI)
- [ ] Refine CLI UX and output consistency
- [ ] Add contribution guide & issue templates
- [ ] Review and clean up public API for long-term maintenance

---

## 🔮 Future Ideas (Long-term Enhancements)

The following enhancements are considered for future development but will be carefully evaluated to avoid making tracelite too heavy or complex. The goal is to keep tracelite lightweight, fast, and developer-friendly.

### ✅ Possible Enhancements (Lightweight & CLI-friendly)
- Multi-source log monitoring
- Log session replay
- Log snapshot & sharing
- CLI history & bookmark
- Webhook integration
- CLI plugin architecture

### ❌ Out of Scope (Heavyweight platform features)
- Remote log streaming over the network
- Centralized log storage and team collaboration features
- Web dashboard interface
- Integration with Prometheus, Grafana, or other monitoring systems
- Machine learning-based anomaly detection

---

**Philosophy:**  
tracelite aims to remain a **lightweight, local-first, CLI log tool** that improves developer experience during testing and debugging.  
Heavyweight features that require server infrastructure, databases, or real-time dashboards will be excluded to avoid unnecessary complexity.
