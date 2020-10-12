from migen import *

# import tinyPlatform

""" ShiftOut
    This reads from memory and shifts out, in parallel, the data for all 8 panels. 
    This needs to shift 64 bits at a max frequency (thoeretically 8MHz) but probably
    more likely <=4MHz.

    The panels will be rewritten to allow an element of PWM fade control of the tubes. 
    Therefore, the panels will be rewritten every 10 ms (100Hz). 
"""
class ShiftOut(Module):
    def __init__(self):
        # Internal signals
        self.PWM_clk = Signal(8) ## Clock to trigger the next shift out. 
        self.PWM_shift = Signal(1) # Flag to trigger shifting out the data
        self.buffer = Signal(64)
        self.buf_cnt = Signal(7)
        # GPIO
        # clock, strobe and OE are shared
        self.clock = Signal()
        self.strobe = Signal()
        self.OE = Signal()
        # Each panel has a separate data line
        self.data1 = Signal()

        
        self.comb += [
            If(self.PWM_clk == 10,
                self.PWM_shift.eq(1),
            )
        ]

        self.sync += [
            self.PWM_clk.eq(self.PWM_clk + 1)
        ]

        self.submodules.shifterFSM = FSM(reset_state='IDLE')

        # IDLE
        self.shifterFSM.act('IDLE',
            If(self.PWM_shift,
                NextValue(self.OE, 0), # Turns all tubes off while we shift out the data. This prevents ghosting
                NextValue(self.buffer, 0xAAAAAAAAAAAAAAAA),
                NextValue(self.buf_cnt, 0),
                NextValue(self.strobe, 1),
                NextState('CLOCK')
            )
        )

        self.shifterFSM.act('CLOCK',
            If(self.clock,
                NextValue(self.clock, 0),
                NextState('DATA') # data read on falling edge, so set data in next state
            ).Else(
                NextValue(self.clock, 1),
                NextState('CLOCK_HOLD')
            )
        )

        self.shifterFSM.act('DATA',
            If((self.buffer & 0x01),
                NextValue(self.data1, 1)
            ).Else(
                NextValue(self.data1, 0)
            ),
            NextValue(self.buf_cnt, self.buf_cnt + 1),
            If(self.buf_cnt == 64,
                NextValue(self.OE, 1), # Turn the tubes back on
                NextValue(self.strobe, 0),
                NextState('IDLE')
            ).Else(
                NextValue(self.buffer, self.buffer >> 1),
                NextState('CLOCK')
            )
        )

        self.shifterFSM.act('CLOCK_HOLD',
            NextState('CLOCK') # This is just a holding state to waste 1 clock
        )


def counter_test(dut):
    for i in range(1000):
        yield # clock the sync

if __name__ == "__main__":
    dut = ShiftOut()
    run_simulation(dut, counter_test(dut), vcd_name="shift.vcd")
