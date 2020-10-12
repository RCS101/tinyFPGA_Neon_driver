from migen import *
# from migen.build.platforms import tinyfpga_a
import tinyPlatform
#from migen.build.generic_platform import Pins, Subsignal, IOStandard

"""
SPI slave in mode:
MSB
polarity 0 = Clock idle low
Phase 2 edge = Data read on falling edge
"""
class SPI(Module):
    def __init__(self, platform):
        self.led0 = led0 = platform.request("user_led0")

        # Input pins
        self.sclk = sclk = platform.request("user_sclk")#Signal()#
        self.mosi = mosi = platform.request("user_mosi")#Signal()#
        self.cs = cs = platform.request("user_cs")#Signal()# =

        self.data = data = Signal(8) # 27 bit LED register
        self.frame_buffer = Signal(8*512) # 512 bytes
        self.error = error = Signal(1)
        self.byte_ack = byte_ack = Signal(1)
        
        self.comb += self.led0.eq(self.byte_ack) # Toggle tinyFPGA led when a byte is acknowledged
        # we are clocked by sclk, every edge run through the FSM

        """
        Implement a finite state machine to handle incoming data
        The SPI slave state machine containts ? states:
        IDLE:
            In IDLE the chip select pin is checked. If chip select is active then the state machine
            moves to DATA.
        START:
        DATA:
            In DATA upon a falling edge on the sclk pin (currently only working in 1 SPI mode) the MOSI
            pin is checked and data added to the data register.
        HOLD:
            In HOLD we wait for the clock to go high
        STOP:
            Wait for data to be handled....???
        """

        self.bit_no = bit_no = Signal(3)
        self.submodules.mosi_fsm = FSM(reset_state="IDLE")

        ### IDLE
        self.mosi_fsm.act("IDLE",
            If(~self.cs, # Active low
                If(~self.byte_ack, # If there is a byte in data, this needs to be read first
                    NextState("START")
                )
            ) # No else. If CS is deactive then we don't do anything!
        )
        ### START
        self.mosi_fsm.act("START",
            If(self.cs,
                NextValue(self.error, self.error + 1),
                NextState("IDLE")
            ).Elif(self.sclk,                #wait until sclk goes low, then move to DATA to read the bit. This is falling edge trigger.
                NextState("DATA")
            )
        )
        ### DATA
        self.mosi_fsm.act("DATA",
            If(self.cs,
                NextValue(self.error, self.error + 1),
                NextState("IDLE")
            ).Elif(~self.sclk,
                NextValue(self.data, Cat(self.data[1:8], self.mosi)), # Cat records the data as LSB - currently don't know how to make it MSB (Im dumb)
                NextValue(bit_no, bit_no + 1),
                If(bit_no == 7,
                    NextState("STOP"),
                    NextValue(self.byte_ack, self.byte_ack + 1)
                    ).Else(
                        NextState("HOLD")
                    )
            )
        )
        ### HOLD
        self.mosi_fsm.act("HOLD",
            If(self.cs,
                NextValue(self.error, self.error + 1),
                NextState("IDLE")
            ).Elif(self.sclk, # wait until the clock goes high again before moving to DATA
                NextState("DATA")
            )
        )
        ### STOP
        self.mosi_fsm.act("STOP",
            ## If either chip is released or the byte is handled return to IDLE
            NextValue(self.byte_ack, 0),
            NextValue(self.data, 0),
            NextState("IDLE")
            # If(self.cs,
            #     NextValue(self.byte_ack, 0),
            #     NextValue(self.data, 0),
            #     NextState("IDLE")
            # )
            # .Elif(~self.byte_ack,
            #     NextState("IDLE")
            # )
        )


""" Function to pretend to be an SPI master sending data """
def _spi_master(tx, dut):
    ## Initialise ports
    print("Initialise")
    yield;
    yield dut.cs.eq(1) # deactive
    yield dut.mosi.eq(0)
    yield dut.sclk.eq(0)
    yield dut.byte_ack.eq(0)
    yield dut.error.eq(0)
    yield; yield; yield; yield; # 4 clocks
    # Set cs active
    yield dut.cs.eq(0)
    yield; yield; yield; yield; # 4 clocks
    # loop through the tx byte setting pins

    bitmask = 0x01 # LSB - make this 0x80 for MSB
    print("Data in: {}".format(hex(tx)))

    for i in range(0, 8):
        if (bitmask & tx) == bitmask:
            yield dut.mosi.eq(1)
        else:
            yield dut.mosi.eq(0)

        bitmask = (bitmask<<1) # flip shift direction for MSB

        yield dut.sclk.eq(1)
        yield; yield; yield; yield;
        yield dut.sclk.eq(0)
        yield; yield; yield; yield;

    yield dut.sclk.eq(0)
    yield dut.mosi.eq(0)
#    yield dut.cs.eq(1)

    yield; yield; yield; yield; # 4 clocks
    yield; yield; yield; yield; # 4 clocks

#    yield dut.cs.eq(0)

    bitmask = 0x01 # LSB - make this 0x80 for MSB
    tx = 0x23
    print("Data in: {}".format(hex(tx)))

    for i in range(0, 8):
        if (bitmask & tx) == bitmask:
            yield dut.mosi.eq(1)
        else:
            yield dut.mosi.eq(0)

        bitmask = (bitmask<<1) # flip shift direction for MSB

        yield dut.sclk.eq(1)
        yield; yield; yield; yield;
        yield dut.sclk.eq(0)
        yield; yield; yield; yield;

    yield dut.sclk.eq(0)
    yield dut.mosi.eq(0)
    yield dut.cs.eq(1)




    print("Transmit complete")
    yield; yield; yield; yield; # 4 clocks
    yield; yield; yield; yield; # 4 clocks

# class TestBench(Module):
#     def __init__(self):

# Create our platform (fpga interface)
plat = tinyPlatform.Platform()
dut = SPI_slave(plat)
run_simulation(dut, _spi_master(0x45, dut), vcd_name="SPI_slave.vcd")

# Create our module and blink LEDs asnd build
# module = SPI_slave(plat)
# plat.build(module)
