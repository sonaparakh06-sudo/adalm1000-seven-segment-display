# adalm1000-seven-segment-display (Python + pysmu)

A counter (00 to 99) that runs automatically from a Python script. The ADALM1000 (M1K) drives a **Shams Power MS-301** 3-digit display board, which has a single **74HC164** shift register and multiplexed digits. No microcontroller is needed.

> Status: 2 digits (right and middle) work. The left digit is planned, using a NOR gate (74HC02) to create the third digit select, since all four digital pins are already used.

<!-- Add a short demo GIF/video here, e.g. ![demo](media/demo.gif) -->

## Hardware

| Part | Notes |
|---|---|
| ADALM1000 (Rev F) | `smu -l` reported hardware F, firmware 2.17 |
| Shams Power MS-301 display board | 3-digit display, one 74HC164, 7-pin connector CN1 |
| Jumper wires, breadboard | |
| 1 kΩ resistor | Only to tie CN1 pin 3 to GND (keeps the left digit off) |

## Wiring (2-digit version)

CN1 pins are counted from the left when the display faces you and "CN1" is above the connector.

| ADALM1000 | CN1 pin | Function |
|---|---|---|
| 3.3 V (digital connector) | 6 | VCC |
| GND | 7 | GND |
| PIO 0 | 4 | DATA |
| PIO 1 | 5 | CLOCK |
| PIO 2 | 1 | Right digit select (direct wire) |
| PIO 3 | 2 | Middle digit select (direct wire) |
| through 1 kΩ to GND | 3 | Left digit select, held off |

The board has no documentation. The pin functions above were found by trial, using a multimeter and test scripts.

### Board behaviour found by testing

- 74HC164 outputs drive the segments in this order (bit 0 to bit 7): **a, f, b, g, c, d, e, dp**
- Segments are **active-low** (a 0 lights a segment).
- Digit selects are **active-high**.
- The decimal point is bit 7 of the same shift register.
- Do not put series resistors on the digit-select lines. With 1 kΩ in series, segments d and e dropped out when many segments were lit, because the select line supplies the current for a whole digit.

## Software setup (Windows)

1. Install the libsmu x64 installer from the [libsmu releases](https://github.com/analogdevicesinc/libsmu/releases) (tick the WinUSB driver option). Version 1.0.4 no longer ships the Python bindings in the Windows installer.
2. Install **64-bit Python 3.10** (the v1.0.4 wheels support Python 3.7 to 3.10 only) and create a virtual environment:
   ```
   py -3.10 -m venv smu-env
   .\smu-env\Scripts\Activate.ps1
   ```
3. Install the pysmu wheel from the release's `libsmu-win32-win64` archive (folder `Windows-VS-16-2019-x64`):
   ```
   python -m pip install path\to\pysmu-1.0.4-cp310-cp310-win_amd64.whl
   ```
4. If `import pysmu` fails with `DLL load failed`, copy `libsmu.dll` and `libusb-1.0.dll` from `C:\Program Files\Analog Devices\libsmu\` into `smu-env\Lib\site-packages\pysmu\`, or add `os.add_dll_directory(...)` at the top of the script (already done in `counter2.py`).
5. Check the board is detected:
   ```
   smu -l
   ```

## Digital pin numbers

In software the four digital pins are not numbered 0 to 3. They are set with `ctrl_transfer`, using these pin numbers (from the [ADI Python tutorial](https://wiki.analog.com/university/tools/python-tutorial/tutorial1-toggle-led?do=)):

| Pin | Software number |
|---|---|
| PIO 0 | 28 |
| PIO 1 | 29 |
| PIO 2 | 47 |
| PIO 3 | 3 |

`0x50` sets a pin low and `0x51` sets it high.

## Run

```
python counter2.py
```

It counts from 0 to 99, holds each number for 1 second, and prints the measured refresh rate. Press Ctrl+C to stop.

## How it works

The 74HC164 has 8 outputs wired to the segments of all three digits in parallel, so only one digit can be lit at a time. The script shifts out the segment pattern for one digit, turns on that digit's select line, then does the same for the next digit, repeatedly. Persistence of vision makes both digits appear lit.

## Known limitations

- Each pin change goes over USB and takes about a millisecond, so the refresh is slow: measured **[fill in] full scans per second**. Expect some flicker and a dimmer display than a normal driver would give.
- The 74HC164 has no latch, so the segments briefly show shifting data while a new pattern is loaded.
- Channel B can't be toggled fast enough to act as the third digit select (it causes a `WriteTimeout`), which is why the left digit needs a NOR gate on PIO 2 and PIO 3.

## Roadmap

- [ ] 3rd digit (left) using a 74HC02 NOR gate on PIO 2 and PIO 3 (select left when both are low)
- [ ] Reduce flicker (for example, an external latch on the shift register)

## Credits

- [libsmu / pysmu](https://github.com/analogdevicesinc/libsmu) by Analog Devices
- ADI wiki: [ADALM1000 digital outputs](https://wiki.analog.com/university/tools/m1k/digital-outputs)
