"""Async wrappers for busio interfaces."""

import busio
import asyncio

if not hasattr(busio.I2C, "dma_write"):
    raise ImportError("This module requires busio with DMA support.")


class I2C(busio.I2C):
    async def lock(self):
        while not self.try_lock():
            await asyncio.sleep(0)

    async def readfrom_into(self, address, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.dma_readinto(address, view, end=True)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def writeto(self, address, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.dma_write(address, view, end=True)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def writeto_then_readfrom(
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

        d = self.dma_write(address, out_view, end=False)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)

        d = self.dma_readinto(address, in_view, end=stop)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(in_view)


class SPI(busio.SPI):
    async def lock(self):
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

        d = self.dma_write_readinto(out_view, in_view)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)

    async def write(self, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.dma_write(view)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def readinto(self, buffer, *, start=0, end=None, write_value=0):
        view = memoryview(buffer)[start:end]
        d = self.dma_readinto(view, write_value=write_value)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(view)


class UART(busio.UART):
    async def lock(self):
        while not self.try_lock():
            await asyncio.sleep(0)

    async def read(self, nbytes=0):
        data = bytearray(nbytes)
        await self.readinto(data)
        return data

    async def readinto(self, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = self.dma_readinto(view)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def write(self, buffer):
        d = self.dma_write(buffer)
        while self.dma_is_busy(d):
            await asyncio.sleep(0)
        return len(buffer)
