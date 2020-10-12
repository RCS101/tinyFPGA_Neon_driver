# tinyFPGA_Neon_driver

Used to drive a 16*32 neon bulb matrix. The neon bulbs are switched using HV5122 32 bit shift registers, PWM is achieved by rewriting the shift 
registers sufficiently fast to achieve 16 levels of brightness.

The shift registers can be driven up to 8MHz but the level shifters limit this to somewhere around a few MHz. A full rewrite takes ? us. 

Since all bulbs are off while data is shift out, the duty cycle for shifting 
wants to be minimised (minimise off time to increase max brightness).
A PWM frequency of x Hz allows for 16 levels of brightness without noticeable flicker

The tinyFPGA acts as a SPI adapter, receiving 512 bytes for neon bulb brightness. Data is shifted out in parallel to all 8 64 bulb panels.
