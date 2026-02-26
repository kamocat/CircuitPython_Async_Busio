import array
import asyncio
import time

import board

import async_busio as busio

uart = busio.UART(board.GP16, board.GP17, baudrate=1200) #Very slow baud rate to emphasize async behavior
async def uarty():


    while True:
        buf = bytearray([0]*100)
        tick = time.monotonic()
        await uart.write(buf)
        #reply = await uart.read(100) #Fixme: What if insufficient bytes are available?
        #await asyncio.sleep(0) #Uncomment if you suspect the driver is not yielding
        tock = time.monotonic()
        print(f"That's me!! {tock-tick}")
        time.sleep(1) #being very busy

async def talker():
    msg = 'Universal Asynchronous Receiver Transmitter'
    while True:
        for s in msg.split():
            print(s)
            await asyncio.sleep(0)
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(uarty(), talker())

asyncio.run(main())
