"""
Arduino LED controller using pyfirmata.

- Connects to an Arduino on a serial COM port (default COM4)
- Exposes led(total) to light up 0..5 LEDs on digital pins [13,12,11,10,9]
- Provides cleanup() to turn off LEDs and close the board connection

Override the COM port by setting the ARDUINO_COMPORT environment variable.
"""
from __future__ import annotations

import atexit
import os
from typing import List, Optional

try:
    import pyfirmata  # type: ignore
except Exception as _e:  # pragma: no cover
    pyfirmata = None  # Will warn on use

# Default configuration
DEFAULT_COMPORT = os.getenv("ARDUINO_COMPORT", "COM4")
LED_PINS: List[int] = [13, 12, 11, 10, 9]

_board: Optional["pyfirmata.Arduino"] = None
_leds: List = []
_warned: bool = False


def _connect_if_needed() -> None:
    """Initialize Arduino board and LED pins if not already connected."""
    global _board, _leds, _warned

    if _board is not None:
        return

    if pyfirmata is None:  # pyfirmata import failed
        if not _warned:
            print("[controller] pyfirmata is not installed. Skipping hardware control.")
            _warned = True
        return

    try:
        _board = pyfirmata.Arduino(DEFAULT_COMPORT)
        # Prepare LED output pins
        _leds = [_board.get_pin(f"d:{pin}:o") for pin in LED_PINS]
        # Ensure all are off initially
        for led_pin in _leds:
            led_pin.write(0)
    except Exception as e:
        if not _warned:
            print(f"[controller] Could not open Arduino on {DEFAULT_COMPORT}: {e}")
            print("[controller] Tip: Check Device Manager for the correct COM port and update ARDUINO_COMPORT.")
            _warned = True
        _board = None
        _leds = []


def led(total: int) -> None:
    """Set the number of LEDs to light.

    total: number of LEDs ON (0..5). Values outside range are clamped.
    """
    _connect_if_needed()

    if not _leds:
        # No board/pins available. No-op with an optional one-time warning.
        return

    try:
        n = int(total)
    except Exception:
        n = 0

    # Clamp to 0..5
    if n < 0:
        n = 0
    if n > len(_leds):
        n = len(_leds)

    for i, led_pin in enumerate(_leds):
        led_pin.write(1 if i < n else 0)


def cleanup() -> None:
    """Turn off LEDs and close the board connection."""
    global _board, _leds

    if _leds:
        for led_pin in _leds:
            try:
                led_pin.write(0)
            except Exception:
                pass

    if _board is not None:
        try:
            _board.exit()
        except Exception:
            pass
        finally:
            _board = None
            _leds = []


# Ensure cleanup on interpreter exit
atexit.register(cleanup)