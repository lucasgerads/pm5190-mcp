# pm5190-mcp

MCP server for controlling the Philips PM5190 LF synthesizer over GPIB.

Connects via any Prologix-compatible USB-to-GPIB adapter (e.g. [AR488](https://github.com/Twilight-Logic/AR488), Prologix GPIB-USB).

## Requirements

- Prologix-compatible USB-to-GPIB adapter
- PM5190 GPIB address configured via DIP switches on the bottom of the unit

## Usage

### From PyPI (recommended)

```bash
uvx pm5190-mcp
PM5190_PORT=/dev/ttyUSB0 PM5190_ADDR=4 uvx pm5190-mcp
```

### From source

```bash
PM5190_PORT=/dev/ttyUSB0 PM5190_ADDR=4 uv run pm5190-mcp
```

### Claude Code configuration

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "pm5190": {
      "type": "stdio",
      "command": "uvx",
      "args": ["pm5190-mcp"],
      "env": {
        "PM5190_PORT": "/dev/ttyUSB0",
        "PM5190_ADDR": "4"
      }
    }
  }
}
```

The GPIB address is set via DIP switches on the bottom of the unit:

![Setting the GPIB address](https://raw.githubusercontent.com/lucasgerads/pm5190-mcp/main/docu/assets/SettingAddress.png)
*Image from the Philips PM5190 user manual.*

## Available tools

| Tool | Description |
|------|-------------|
| `pm5190_connect` | Connect to the USB-to-GPIB adapter |
| `pm5190_disconnect` | Disconnect |
| `pm5190_status` | Connection status and firmware version |
| `pm5190_configure` | Set frequency, amplitude, DC offset and waveform in one command |
| `pm5190_set_frequency` | Set frequency only |
| `pm5190_set_amplitude` | Set amplitude and DC offset |
| `pm5190_set_waveform` | Set waveform type |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PM5190_PORT` | — | Serial port (auto-connects on startup if set) |
| `PM5190_BAUD` | `115200` | Baud rate |
| `PM5190_ADDR` | `4` | GPIB address |
