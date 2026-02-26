import array
import asyncio
import time

import board

import async_busio as busio

spi = busio.SPI(board.GP2, board.GP3, board.GP4)

async def spier():

    
    register = bytearray([0x00])
    data = bytearray(1)
    while True:
        await spi.lock()
        buf = array.array('h', list(range(1000)))
        tick = time.monotonic()
        for i in range(10):
            await spi.write_readinto(buf, buf)
        #await asyncio.sleep(0) #Uncomment if you suspect the driver is not yielding
        tock = time.monotonic()
        spi.unlock()
        print(f'Harumph {tock-tick} ')
        #time.sleep(1) #being very busy

async def talker():
    msg = 'Hi there SPI!'
    while True:
        for s in msg.split():
            print(s)
            await asyncio.sleep(0)
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(spier(), talker())

asyncio.run(main())