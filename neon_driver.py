from migen import *
from shift_out import *
from spi_receiver import *


class PWM_stripper(Module):
    def __init__(self, data):
        # FSM to run through the data for each panel and generate a PWM mask
        # There will be an instance of this for each panel. 
        self.submodules.PMW_fsm = FSM(reset_state='IDLE')

        self.PWM_fsm.act('IDLE',
            NextState('MASK')
        )

        self.PWM_fsm.act('MASK',

        )

class Neon_driver(Module):
    def __init(self):
        # PWM clock
        self.clk = Signal(10)

        self.bitmask = Signal(8)


        spi = SPI()
        shifter = ShiftOut()
        self.submodules += spi
        self.submodules += shifter

        # Data buffers
        self.back_buffer = Signal(8*512) # Data streaming in from SPI
       
        # Panel data channels
        self.panel1 = Array(Signal(8) for _ in range(64)) 
        self.panel_backbuffer = Signal(64)
        self.panel_shift = Signal(64)

        # Flags
        self.SPI_complete = Signal()

        # Link signals
        self.back_buffer = spi.frame_buffer
        self.panel_buffer1 = self.panel_shift # panel_buffer1 is what is shift out on this update of the PWM.

        self.comb += [ 
            If(self.clk == 1,
                If((self.panel1[0]),
                    self.panel_shift
                )
            )
        ]

        self.sync += [
            self.clk.eq(self.clk + 1)
        ]

        