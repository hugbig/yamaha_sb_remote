# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2026-11-23

### Changed

- One Bluetooth connection per update for all five entities, instead of one per entity. The state
  is read once at startup, then every 30 seconds when *Auto polling for update* is on. Thanks
  @SuperTux88 for the idea (#6).
- Commands read the state back in the same connection, so every entity shows it at once. A
  subwoofer change sends all its steps in one connection.
- When the soundbar does not answer twice in a row, the entities become unavailable and the
  integration tries again every 60 seconds. At startup, the integration shows "retrying setup"
  until the soundbar answers.
- A command that cannot reach the soundbar now shows an error instead of failing silently.
- Entity names no longer repeat the device name, for example *Yamaha SR-C20A LED* instead of
  *Yamaha SR-C20A Yamaha SR-C20A_led*. Existing entity ids are kept.
- Home Assistant 2024.11 or later is required.

### Fixed

- Commands and status frames whose checksum is 0x00: building such a command crashed, and such a
  frame was rejected as a bad checksum.
- An unknown value in the status frame no longer raises an error; that value is shown as unknown.
- The integration can be reloaded or removed without restarting Home Assistant.

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
