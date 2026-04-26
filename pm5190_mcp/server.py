"""MCP server for the Philips PM5190 LF synthesizer via AR488 serial-to-GPIB adapter."""

import os
import threading
from mcp.server.fastmcp import FastMCP
from pm5190_mcp.instrument import PM5190, PM5190Error

mcp = FastMCP("pm5190")

_gen = PM5190()
_lock = threading.Lock()


def _run(fn):
    try:
        with _lock:
            return fn()
    except PM5190Error as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


# Auto-connect on startup if PM5190_PORT is set
_port = os.environ.get("PM5190_PORT")
if _port:
    _baud = int(os.environ.get("PM5190_BAUD", "115200"))
    _addr = int(os.environ.get("PM5190_ADDR", "4"))
    try:
        firmware = _gen.connect(_port, _baud, _addr)
        print(f"Connected to PM5190 on {_port} — {firmware}")
    except PM5190Error as e:
        print(f"Auto-connect failed: {e}")


@mcp.tool()
def pm5190_connect(
    port: str = "/dev/ttyUSB0",
    baud: int = 115200,
    gpib_addr: int = 4,
) -> str:
    """Connect to the PM5190 via an AR488 serial-to-GPIB adapter.

    Args:
        port:       Serial port the AR488 is on, e.g. /dev/ttyUSB0
        baud:       Baud rate (default 115200)
        gpib_addr:  GPIB address of the PM5190 (default 4, set via DIP switches on unit bottom)
    """
    def _fn():
        firmware = _gen.connect(port, baud, gpib_addr)
        return f"Connected on {port} — {firmware}"
    return _run(_fn)


@mcp.tool()
def pm5190_disconnect() -> str:
    """Disconnect from the PM5190."""
    def _fn():
        _gen.disconnect()
        return "Disconnected"
    return _run(_fn)


@mcp.tool()
def pm5190_status() -> str:
    """Return current connection status and AR488 firmware version."""
    def _fn():
        if _gen.is_connected:
            return f"Connected — port: {_gen.port}, baud: {_gen.baud}, GPIB addr: {_gen.gpib_addr}, firmware: {_gen.firmware}"
        return "Not connected"
    return _run(_fn)


@mcp.tool()
def pm5190_configure(
    freq_hz: float,
    vpp: float,
    dc: float = 0.0,
    waveform: int = 1,
) -> str:
    """Set all PM5190 parameters in a single command.

    Args:
        freq_hz:   Frequency in Hz (range: 0.001 – 2000000)
        vpp:       Output amplitude peak-to-peak in volts (range: 0.001 – 19.9)
        dc:        DC offset in volts (default 0.0; range depends on amplitude)
        waveform:  Waveform type: 1=sine, 2=square, 3=square, 4=sine/AM ext, 5=triangle/AM ext

    The maximum DC offset depends on the amplitude range:
      - Vpp < 0.2 V:  max |DC| ≈ 0.1 V
      - Vpp < 2.0 V:  max |DC| ≈ 1.0 V
      - Vpp ≤ 19.9 V: max |DC| ≈ 10.0 V
    """
    def _fn():
        cmd = _gen.configure(freq_hz, vpp, dc, waveform)
        wf_name = PM5190.WAVEFORMS.get(waveform, f"W{waveform}")
        return f"Set: {freq_hz} Hz, {vpp} Vpp, {dc} V DC, {wf_name} — sent: {cmd}<ETX>"
    return _run(_fn)


@mcp.tool()
def pm5190_set_frequency(freq_hz: float) -> str:
    """Set the output frequency without changing other parameters.

    Args:
        freq_hz:  Frequency in Hz (range: 0.001 – 2000000). Dimension is always kHz on the bus.
    """
    def _fn():
        cmd = _gen.set_frequency(freq_hz)
        return f"Frequency set to {freq_hz} Hz — sent: {cmd}<ETX>"
    return _run(_fn)


@mcp.tool()
def pm5190_set_amplitude(vpp: float, dc: float = 0.0) -> str:
    """Set the output amplitude and DC offset.

    Amplitude and DC offset must always be set together because the DC offset
    encoding depends on the amplitude range.

    Args:
        vpp:  Output amplitude peak-to-peak in volts (range: 0.001 – 19.9)
        dc:   DC offset in volts (default 0.0)
    """
    def _fn():
        cmd = _gen.set_amplitude(vpp, dc)
        return f"Amplitude set to {vpp} Vpp, DC offset {dc} V — sent: {cmd}<ETX>"
    return _run(_fn)


@mcp.tool()
def pm5190_set_waveform(waveform: int) -> str:
    """Set the output waveform type without changing other parameters.

    Args:
        waveform:  1=sine, 2=square, 3=triangle, 4=sine/AM ext, 5=triangle/AM ext
    """
    def _fn():
        if waveform not in PM5190.WAVEFORMS:
            raise PM5190Error(f"Invalid waveform {waveform}, must be 1–5")
        cmd = _gen.set_waveform(waveform)
        return f"Waveform set to {PM5190.WAVEFORMS[waveform]} — sent: {cmd}<ETX>"
    return _run(_fn)


def main():
    mcp.run(transport="stdio")
