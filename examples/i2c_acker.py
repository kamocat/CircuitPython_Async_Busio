import board
import adafruit_pioasm
import rp2pio
import time


PROGRAM = """
.program i2c_always_ack

.wrap_target
start_wait:
	; Wait for START: SCL high and SDA low
	wait 1 pin 0
	jmp pin start_wait

byte_start:
	mov isr, null
	set y, 7
bitloop:
	; Sample 8 data bits on SCL high and shift into ISR.
	wait 1 pin 0
	set x, 0
	jmp pin data_high
data_sampled:
	in x, 1
	wait 0 pin 0
	jmp y-- bitloop

	; ACK bit: drive SDA low for 9th clock
	set pindirs, 1
	wait 1 pin 0
	wait 0 pin 0
	set pindirs, 0
	push block

	; STOP/idle detection: if SCL high and SDA high, wait for next START
	wait 1 pin 0
	jmp pin start_wait
	; Otherwise SDA low while SCL high (repeated START/continued frame)
	jmp byte_start

data_high:
	set x, 1
	jmp data_sampled
.wrap
"""


def main(scl=board.GP21, sda=board.GP20):
	assembled = adafruit_pioasm.assemble(PROGRAM)

	sm = rp2pio.StateMachine(
		assembled,
		frequency=2_000_000,
		first_in_pin=scl,
		in_pin_count=1,
		jmp_pin=sda,
		first_set_pin=sda,
		set_pin_count=1,
		initial_set_pin_state=0,
		initial_set_pin_direction=0,
		auto_pull=False,
		auto_push=False,
		in_shift_right=False,
	)

	print("PIO I2C ACK helper running")
	print("SCL:", scl, "SDA:", sda)
	print("ACKs each byte on the 9th clock during active I2C frames")
	print("START/STOP detected using SDA level while SCL is high")
	print("Received bytes are pushed to the PIO RX FIFO")
	print("Press Ctrl-C to stop")

	try:
		buf = bytearray(1)
		while True:
			sm.readinto(buf)
			print(f"rx: 0x{buf[0]:02x}")
	finally:
		sm.deinit()


main()

