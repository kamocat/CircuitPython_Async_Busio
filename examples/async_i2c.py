import array
import asyncio
import time

import board

import abusio

addr = None
i2c = abusio.I2C(board.GP21, board.GP20)

async def icer():

    
    register = bytearray([0x00])
    data = bytearray(1)
    while True:
        await i2c.alock()
        bin = array.array('h', [1]*8)
        bout = array.array('b', [0]*16)
        tick = time.monotonic()
        await i2c.writeto(addr, bout)
        await i2c.areadfrom_into(addr, bin)
        #await asyncio.sleep(0) #Uncomment if you suspect the driver is not yielding
        tock = time.monotonic()
        i2c.unlock()
        print(f'Hush! I am very busy! {tock-tick} ')
        time.sleep(1) #being very busy

async def talker():
    msg = 'But what about MEEE ??!'
    while True:
        for s in msg.split():
            print(s)
            await asyncio.sleep(0)
        await asyncio.sleep(1)

async def main():
    global addr
    await i2c.alock()
    found = i2c.scan() #This one is not async
    i2c.unlock()
    if len(found) == 0:
        raise RuntimeError("This example expects an I2C device")
    addr = found[0]
    await asyncio.gather(icer(), talker())

asyncio.run(main())
