"""Async wrappers for busio interfaces."""

import busio
import asyncio


class I2C(busio.I2C):
    async def lock(self):
        while not self.try_lock():
            await asyncio.sleep(0)

    async def readfrom_into(self, address, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = busio.dma.i2c_read(self, address, view, end=True)
        while busio.dma.i2c_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def writeto(self, address, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = busio.dma.i2c_write(self, address, view, end=True)
        while busio.dma.i2c_is_busy(d):
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

        d = busio.dma.i2c_write(self, address, out_view, end=False)
        while busio.dma.i2c_is_busy(d):
            await asyncio.sleep(0)

        d = busio.dma.i2c_read(self, address, in_view, end=stop)
        while busio.dma.i2c_is_busy(d):
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

        d = busio.dma.spi_write_readinto(self, out_view, in_view)
        while busio.dma.spi_is_busy(d):
            await asyncio.sleep(0)

    async def write(self, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = busio.dma.spi_write(self, view)
        while busio.dma.spi_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def readinto(self, buffer, *, start=0, end=None, write_value=0):
        view = memoryview(buffer)[start:end]
        d = busio.dma.spi_readinto(self, view, write_value=write_value)
        while busio.dma.spi_is_busy(d):
            await asyncio.sleep(0)
        return len(view)


class UART(busio.UART):
    async def lock(self):
        while not self.try_lock():
            await asyncio.sleep(0)

    async def read(self, nbytes=None):
        if nbytes is None:
            return busio.UART.read(self, nbytes)

        if nbytes <= 0:
            return b""

        data = bytearray(nbytes)
        await self.readinto(data)
        return data

    async def readinto(self, buffer, *, start=0, end=None):
        view = memoryview(buffer)[start:end]
        d = busio.dma.uart_readinto(self, view)
        while busio.dma.uart_is_busy(d):
            await asyncio.sleep(0)
        return len(view)

    async def write(self, buffer):
        d = busio.dma.uart_write(self, buffer)
        while busio.dma.uart_is_busy(d):
            await asyncio.sleep(0)
        return len(buffer)
