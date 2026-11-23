<h1 align="center">Yamaha soundbar (Bluetooth) for Home Assistant</h1>

<p align="center">
  <a href="https://github.com/hugbig/yamaha_sb_remote/actions/workflows/tests.yml"><img src="https://github.com/hugbig/yamaha_sb_remote/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/hugbig/yamaha_sb_remote/actions/workflows/validate.yaml"><img src="https://github.com/hugbig/yamaha_sb_remote/actions/workflows/validate.yaml/badge.svg" alt="Validate"></a>
  <a href="https://github.com/hugbig/yamaha_sb_remote/releases/latest"><img src="https://img.shields.io/github/v/release/hugbig/yamaha_sb_remote" alt="Latest release"></a>
  <a href="https://hacs.xyz"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5" alt="HACS Custom"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2024.11%2B-41BDF5" alt="Home Assistant 2024.11+">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/hugbig/yamaha_sb_remote" alt="License: MIT"></a>
</p>

Control a Yamaha soundbar from Home Assistant over Bluetooth Low Energy, using the same protocol as
the Yamaha *Sound Bar Remote* app. It works with a local Bluetooth adapter or an ESPHome Bluetooth
proxy. There is no cloud service.

> **Unofficial community integration.** It is not affiliated with, endorsed by, or supported by
> Yamaha.

## What it does

One device with five entities:

| Entity | Controls |
|---|---|
| Media player | Power, source (Bluetooth, TV, Optical, Analog), volume, mute, sound mode (Standard, Movie, Game) |
| Switch *Clear Voice* | Clear Voice on/off |
| Switch *Bass Extension* | Bass Extension on/off |
| Number *Subwoofer* | Subwoofer level, from −4 to 4 |
| Select *LED* | Front LED brightness: Bright, Dim, Off |

## Tested soundbar

- Yamaha **SR-C20A**

Other Yamaha soundbars that work with the Sound Bar Remote app may work too. Please open an issue
to report yours.

## Requirements

- Home Assistant 2024.11 or later.
- A Bluetooth adapter on the Home Assistant host, or an
  [ESPHome Bluetooth proxy](https://esphome.io/projects/?type=bluetooth), within range of the
  soundbar. The proxy must allow active connections (`bluetooth_proxy: active: true`).
- The soundbar's Bluetooth MAC address.

## Installation

### HACS

1. In HACS, add `https://github.com/hugbig/yamaha_sb_remote` as a custom repository of type
   *Integration*.
2. Install **yamaha_sb_remote** and restart Home Assistant.

### Manual

Copy `custom_components/yamaha_sb_remote` into the `custom_components` folder of your Home
Assistant configuration, then restart Home Assistant.

## Configuration

Go to **Settings → Devices & services → Add integration**, search for **yamaha_sb_remote** and fill
in:

- **Mac Adress**: the soundbar's Bluetooth MAC address, for example `AA:BB:CC:DD:EE:FF`;
- **Name**: the device name in Home Assistant;
- **Auto polling for update**: when on, the state is read every 30 seconds, so changes made with
  the Yamaha remote or app show up. When off, it is read at startup and after each command.

All five entities share one Bluetooth connection per update. If the soundbar does not answer, the
entities become unavailable and the integration tries again every 60 seconds.

## Troubleshooting

- **Turn on debug logs** from the integration page (**Enable debug logging**). The logs then show
  every frame received from the soundbar.
- **"No backend with an available connection slot that can reach address …"**: no Bluetooth
  adapter or proxy can connect to the soundbar. Move a proxy closer, check that it allows active
  connections, or free a connection slot.

## Development

Python 3.14 is required (the version Home Assistant's test package uses):

```sh
pip install -r requirements-test.txt
ruff check .
pytest
```

The tests run against a fake soundbar that speaks the BLE protocol, so no hardware is needed. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
