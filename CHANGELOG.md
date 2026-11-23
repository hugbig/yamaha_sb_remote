# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- Commands and status frames whose checksum is 0x00: building such a command crashed, and such a
  frame was rejected as a bad checksum.

## [1.1.0] - 2026-11-23

First tagged release. Earlier versions were installed from `main` and all reported 1.0.0.

### Fixed

- The media player platform failed to load (`async_setup_entry` was not a coroutine).
  Thanks @SuperTux88 (#6).
- BLE calls no longer block: a soundbar that Home Assistant cannot see is skipped with a warning,
  and the wait for the status notification gives up after 5 seconds. Thanks @SuperTux88 (#6).
- Connections go through `bleak_retry_connector.establish_connection`, which retries transient
  errors such as those seen through ESPHome proxies, and are always released after an error.
  Thanks @SuperTux88 (#6).

### Changed

- README rewritten, code owner corrected to @hugbig.
