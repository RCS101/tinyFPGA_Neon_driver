# tinyFPGA_Neon_driver

Used to drive a 16*32 neon bulb matrix. The neon bulbs are switched using HV5122 32 bit shift registers, PWM is acheived by rewriting the shift 
registers sufficiently fast to achieve 16 levels of brightness.

The shift registers can be driven up to 8MHz but the level shifters limit this to somewhere around a few MHz. A full rewrite takes? us. 

The tinyFPGA acts as a SPI adapter, recieving 512 bytes for neon bulb brightness. Data is shifted out in parallel to all 8 64 bulb panels.
