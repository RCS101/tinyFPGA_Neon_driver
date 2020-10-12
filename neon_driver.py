from migen import *
from shift_out import *
from spi_reciever import *

class Neon_driver(Module):
    def __init(self):

        spi = SPI()
        shifter = ShiftOut()
        self.submodules += spi
        self.submodules += shifter

        # Data buffers
        self.back_buffer = Signal(8*512) # Data streaming in from SPI
       
        # Panel data channels
        self.data1 = Signal(64*8)

        # Flags
        self.SPI_complete = Signal()

        # Link signals
        self.back_buffer = spi.frame_buffer
        self.data1 = 

        self.comb += [ 
            If(self.SPI_complete,
                self.data1.eq(self.back_buffer & 0xffffffffffffffff), # mask off the first 64 bytes
                # self.data2.eq((self.back_buffer >> 64*8) & 0xffffffffffffffff),
                # self.data3.eq((self.back_buffer >> 2*(64*8)) & 0xffffffffffffffff),
                self.SPI_complete.eq(0)
            )
        ]

