"""Async wrappers for busio interfaces."""

import busio
import asyncio

if not hasattr(busio.I2C, "start_write"):
    raise ImportError("This module requires busio with DMA support.")


class I2C(busio.I2C):
    async def alock(self):
        while not self.try_lock():
            await asyncio.sleep(0)

    async def areadfrom_into(self, address, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.start_read(address, view, nostop=nostop)
        while self.read_isbusy(d):
            await asyncio.sleep(0)
        return len(view)

    async def writeto(self, address, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.start_write(address, view, nostop=nostop)
        while self.write_isbusy(d):
            await asyncio.sleep(0)
        return len(view)

    async def awriteto_then_readfrom(
        self,
        address,
        out_buffer,
        in_buffer,
        *,
        out_start=0,
        out_end=None,
        in_start=0,
        in_end=None,
        stop=False,
    ):
        out_view = memoryview(out_buffer)[out_start:out_end]
        in_view = memoryview(in_buffer)[in_start:in_end]

        d = self.start_write(address, out_view, nostop=True)
        while self.write_isbusy(d):
            await asyncio.sleep(0)

        d = self.start_read(address, in_view, nostop=not stop)
        while self.read_isbusy(d):
            await asyncio.sleep(0)
        return len(in_view)


class SPI(busio.SPI):
    async def alock(self):
        while not self.try_lock():
            await asyncio.sleep(0)

    async def awrite_readinto(
        self,
        out_buffer,
        in_buffer,
        *,
        out_start=0,
        out_end=None,
        in_start=0,
        in_end=None,
    ):
        out_view = memoryview(out_buffer)[out_start:out_end]
        in_view = memoryview(in_buffer)[in_start:in_end]

        if len(out_view) != len(in_view):
            raise ValueError("buffer slices must be same length")

        d = self.start_transfer(out_view, in_view)
        while self.transfer_isbusy(d):
            await asyncio.sleep(0)

    async def awrite(self, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.start_transfer(view, None)
        while self.transfer_isbusy(d):
            await asyncio.sleep(0)
        return len(view)

    async def areadinto(self, buffer, *, start=0, end=None, write_value=0):
        view = memoryview(buffer)[start:end]
        d = self.start_transfer(None, view)
        while self.transfer_isbusy(d):
            await asyncio.sleep(0)
        return len(view)


class UART(busio.UART):

    async def aread(self, nbytes=0):
        buf = bytearray()
        while nbytes > 0:
            if self.in_waiting == 0:
                await asyncio.sleep(0)
                continue
            n = min(nbytes, self.in_waiting)
            buf.extend(self.read(n))
            nbytes -= n
        return buf

    async def awrite(self, buffer):
        d = self.start_write(buffer)
        while self.write_isbusy(d):
            await asyncio.sleep(0)
        return len(buffer)
