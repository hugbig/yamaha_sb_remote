"""A fake Yamaha soundbar for the tests.

The status frame is built from the byte layout observed on a real SR-C20A, without using
the integration's own encoder or decoder, so the tests can catch mistakes in either.
"""

import asyncio
from dataclasses import dataclass


@dataclass
class SoundbarState:
    """What the soundbar reports in its status frame."""

    power: bool = False
    source: int = 0x07  # TV
    muted: bool = False
    volume: int = 20
    sub: int = 16  # raw code, 0..32 in steps of 4; 16 is level 0
    style: int = 0x0A  # Standard
    clear_voice: bool = False
    bass_ext: bool = False
    led: int = 0  # 0 Bright, 1 Dim, 2 Off


def frame(payload: bytes) -> bytes:
    """Wrap a payload as CC AA <length> <payload> <checksum>."""
    body = bytes([len(payload)]) + payload
    return b"\xcc\xaa" + body + bytes([(-sum(body)) & 0xFF])


def build_status_frame(state: SoundbarState) -> bytes:
    """The 18-byte status frame the soundbar sends after a status request."""
    flags = (0x04 if state.clear_voice else 0) | (0x20 if state.bass_ext else 0)
    payload = bytes(
        [
            0x05,
            0x00,
            0x11 if state.power else 0x10,
            state.source,
            0x01 if state.muted else 0x00,
            state.volume,
            state.sub,
            0x20,
            0x20,
            0x00,
            0x01,
            state.style,
            flags,
            state.led,
        ]
    )
    return frame(payload)


# Command payloads (between the length byte and the checksum), as sent by the Yamaha app.
SOURCES = {0x29: 0x05, 0xDF: 0x07, 0x49: 0x0A, 0xD1: 0x0C}
STYLES = {0xD9: 0x03, 0xDC: 0x0C}


class FakeSoundbar:
    """Stands in for the BleakClient that establish_connection returns."""

    def __init__(self, state: SoundbarState | None = None) -> None:
        self.state = state or SoundbarState()
        self.written: list[bytes] = []
        self.connected = False
        self.disconnect_calls = 0
        # Failure modes
        self.reachable = True
        self.answer_status = True
        self.connect_error: Exception | None = None
        self.frame_override: bytes | None = None
        self.events_before_status: list[bytes] = []
        self.fail_next = 0  # number of status requests to ignore
        self.answer_after_commands = True  # answer status requests that follow a command
        self._commanded = False
        self._callback = None

    async def connect(self) -> "FakeSoundbar":
        if self.connect_error is not None:
            raise self.connect_error
        self.connected = True
        return self

    async def start_notify(self, uuid, callback) -> None:
        self._callback = callback
        self._commanded = False

    async def write_gatt_char(self, uuid, data) -> None:
        data = bytes(data)
        self.written.append(data)
        payload = data[3:-1]
        if payload == b"\x03\x05":
            if self._commanded and not self.answer_after_commands:
                return
            if self.fail_next:
                self.fail_next -= 1
                return
            if self.answer_status and self._callback is not None:
                status = self.frame_override or build_status_frame(self.state)
                loop = asyncio.get_running_loop()
                for event in self.events_before_status:
                    loop.call_soon(self._callback, None, bytearray(event))
                loop.call_soon(self._callback, None, bytearray(status))
            return
        self._commanded = True
        self._apply(payload)

    async def disconnect(self) -> None:
        self.disconnect_calls += 1
        self.connected = False

    def _apply(self, payload: bytes) -> None:
        state = self.state
        if payload[0] == 0x41:
            state.volume = payload[1]
        elif payload[0] == 0x51:
            state.led = payload[1]
        elif payload[:2] == b"\x40\x78":
            code = payload[2]
            if code in (0x7E, 0x7F):
                state.power = code == 0x7E
            elif code in SOURCES:
                state.source = SOURCES[code]
            elif code == 0x4C:
                state.sub = min(state.sub + 4, 32)
            elif code == 0x4D:
                state.sub = max(state.sub - 4, 0)
            elif code in STYLES:
                state.style = STYLES[code]
            elif code in (0x6E, 0x6F):
                state.bass_ext = code == 0x6E
        elif payload[:2] == b"\x40\x7e":
            code = payload[2]
            if code in (0xA2, 0xA3):
                state.muted = code == 0xA2
            elif code == 0xF1:
                state.style = 0x0A
            elif code in (0x80, 0x82):
                state.clear_voice = code == 0x80
