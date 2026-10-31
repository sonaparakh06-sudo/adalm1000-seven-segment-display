import os, time
os.add_dll_directory(r"C:\Program Files\Analog Devices\libsmu")
from pysmu import Session

DATA, CLK = 28, 29          # PIO 0, PIO 1
SEL_R, SEL_M = 47, 3        # PIO 2 = right digit, PIO 3 = middle digit
HOLD = 1.0                  # seconds each number stays on the display

# bit0=a, bit1=f, bit2=b, bit3=g, bit4=c, bit5=d, bit6=e, bit7=dp
MASK = [0x77, 0x14, 0x6D, 0x3D, 0x1E, 0x3B, 0x7B, 0x15, 0x7F, 0x3F]

session = Session()
dev = session.devices[0]
session.start(0)
time.sleep(0.3)

def pin(n, level):
    dev.ctrl_transfer(0x40, 0x51 if level else 0x50, n, 0, 0, 0, 100)

def send(byte):
    for i in range(7, -1, -1):          # MSB first
        pin(DATA, (byte >> i) & 1)
        pin(CLK, 1)
        pin(CLK, 0)

def show(n, seconds):
    tens, ones = (n // 10) % 10, n % 10
    end, scans = time.time() + seconds, 0
    while time.time() < end:
        pin(SEL_R, 0); pin(SEL_M, 0)    # blank while shifting
        send(~MASK[tens] & 0xFF)        # segments are active-low
        pin(SEL_M, 1)
        pin(SEL_R, 0); pin(SEL_M, 0)
        send(~MASK[ones] & 0xFF)
        pin(SEL_R, 1)
        scans += 1
    return scans / seconds

try:
    for n in range(100):
        rate = show(n, HOLD)
        print(n, f"({rate:.1f} scans/s)")
except KeyboardInterrupt:
    pass
finally:
    pin(SEL_R, 0); pin(SEL_M, 0)
    session.end()