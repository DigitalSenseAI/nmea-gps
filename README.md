# gps-nmea

`gps-nmea` is a lightweight Python package to read and parse **NMEA** sentences from Garmin 18x (and compatible GPS receivers) over serial communication.

It focuses on practical GPS ingestion with support for common sentence types (`GGA`, `RMC`) and a simple API to get structured data from live serial input.

## Features

- Read GPS data from serial device (`pyserial`)
- Decode NMEA sentences
- Parse `GGA` and `RMC` messages
- Validate message integrity before parsing
- Configurable read strategy:
  - `block`: wait until expected message type arrives
  - `yield`: return parsed data only if current line matches, otherwise `{}`

## Installation

### From source

```bash
pip install -e .
```

### With dev dependencies

```bash
pip install -e ".[dev]"
```

## Quick start

```python
from gps_nmea import GPS_connector

gps = GPS_connector(
    src="/dev/ttyACM0",
    baudrate=4800,
    message_type="GGA",
    strategy="block",
)

data = gps.get_data()
print(data)
```

## Run tests

```bash
python3 -m pytest -q
```

## Project structure

- `gps_nmea/connector.py`: serial connection and NMEA parsing logic
- `tests/`: unit tests

## Notes

- Default serial source is `/dev/ttyACM0` (Linux).
- Current API exports `GPS_connector` for compatibility.
- Python package name: `gps-nmea`
- Import package: `gps_nmea`

# TODO

## High priority

- [ ] Add complete usage examples in README (GGA and RMC)
- [ ] Add CI workflow
    - [ ] Add `flake8`
    - [ ] Add tests
- [ ] Add serial timeout and retry limit to avoid infinite blocking
- [ ] Add unit tests for `get_data()` using mocked `serial.Serial`

## Parsing and validation

- [ ] Add stricter NMEA checks:
  - [ ] minimum field count validation
  - [ ] checksum validation (`*XX`)
- [ ] Add tests for invalid bytes and decode failures

## Testing

- [ ] Add tests for unknown fix/status values
- [ ] Add tests for strategy behavior:
  - [ ] `yield` returns `{}` for non-matching messages
  - [ ] `block` waits until matching message type appears

## Documentation

- [ ] Add troubleshooting section (permissions, serial device path, baudrate)
