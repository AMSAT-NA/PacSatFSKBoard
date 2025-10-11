PacSat AFSK Board Interface Control Document
============================================

Oct 10, 2024
Revision: 0.1

## Version History

| Revision | Date         | Author(s)         | Change Log |
|--------- |------------- |--------------	  |----------- |
| 0.1      | Oct 10, 2024 | C Minyard (AE5KM) | Initial Revision|

# Introduction

This document describes how the PacSat AFSK board interfaces with
other boards and system components of a satellite.

# System Description

The figure below show the block diagram of the PacSatAFSK board:

![Alt text](PacSatAFSK-BlockDiagram.svg "PacSat AFSK Board Block Diagram")

Not show are control and telemetry lines from the CPU to various parts
of the system and clock distribution, as that would clutter the
diagram unnecessarily.  Temperature measuring devices, for example.

The top of the diagram shows connections to the PC104 connector, the
bottom shows RF connections to antennas and to the redundant board.

## Power Supply

The power supply takes 5V and optionally 3.3V and uses that to supply
the rest of the board.  If 3.3V is not externally supplied, a buck
regulator is available to convert 5V to 3.3V.  Power inputs have
inductors to control surge current on power up.

An external power disable line, HW\_POWER\_OFF\_N, is supplied to
power down all parts of the board except for +5VAL, as described
below.

The UMBILICAL\_ATTACHED goes to the processor, but also hard disables
the power to the PA.

The power supply has separate power zones for different parts of the
board.  These are:

* +5V - The main power input for 5V.

* +5VAL - This provides +5V whenever power is applied.  It is used to
  power the batter input for the RTC, the RX/TX switches (so the
  redundant board can access the antenna even if this power is powered
  off), the switches on the dual-board control lines (so the other board
  can control and access this board even when this board is powered
  off), and the CAN bus transceivers (so they can properly go tristate
  even if the board is off).  This is current limited to 200ma.
  
* +1.2V - Main power for the CPU.  HW\_POWER\_OFF\_N will disable
  this.  This is regulated to 700ma maximum.  Power comes from a buck
  regulator (either 5V or 3.3v depending on configuration).

* REG_3.3V - Either the 3.3V externally, or the output of the 3.3V buck
  regulator, depending on how the board is configured.  This is used
  for some control and the watchdog timer so they are available even
  when the board is powered off by the WDT.
  
* +3.3V - This is the man I/O supply for the CPU and power for the
  MRAMs and the RTC.  It is current limited to 640ma.
  
* AX5043_3.3V - This is a separately switched power, off by default,
  that powers all the AX5043 chips.  The CPU must enable power to
  these through a GPIO.  This is current limited to 200ma.
  
* SPPA_VCC - This is +5V to the PA.  This is off by default and the
  CPU must enable it with a GPIO before it can transmit.  In addition,
  as mentioned before, UMBILICAL\_ATTACHED will disable this.  This is
  current limited to 640ma.
  
* LNA_VCC - This is +5V to the LNA.  This is off by default and the
  CPU must enable it with a GPIO before it can receive.  This is
  current limited to 200ma.

In addition, each AX5043 has a separate power control line from the
CPU.

## Temperature Measurement

Three temperature sensors are on the board, one by the CPU, one in the
power supply, and one near the PA.  These are thermsistors that feed
into A/D converters on the CPU.

## CPU

The TI Hercules CPU, a TMS5700914APGEQQ1 specifically, is a CPU
designed for automotive use.  It has two ARM Cortex-M4F processors
running in lockstep for detection of errors.  It does not have the
ability to split the CPUs for independent execution, the dual CPUs are
only used for lockstep processing.  It provides the I2C, SPI, and
GPIOs for controlling the rest of the board, and the CAN bus and GPIOs
for communicating off the board.

### CAN

The CAN bus is an automotive communication bus designed for harsh
environments.  It is used to communicate off the board.  Two CAN
busses are available.

### MRAM

2MB of MRAM is available on one of the SPI busses for storage of state
information.

### RTC

A real-time clock is available so the board has accurate time even
when off.  The battery input comes from +5VAL, and this has a large
diode-protected capacitor so that even if external power is not
available time can be kept for a few days.

### WDT

A watchdog timer on the board will power-cycle the CPU by disabling
+1.2V and +3.3V if the CPU does not toggle its FEED line once a
second.  Powering off the CPU will cause all other power except
REG_3.3V and +5VAL to be returned to their default, disabled, so it
effectively powers off the whole board.

## RX

The RF subsection consists of the section used for receiving signals.
It can receive on 4 different frequencies simultaneously.

### LPF

The Low Pass Filter on the antenna input keeps 440MHz from the
transmitter out of the receiver.  It has a relatively low loss (<1dB)
to keep the sensitivity of the receiver high.  It's cutoff is 176MHz.

### LNA

The Low Noise Amplifier provides ~20dB of gain to the input signal
from the LPF.

### BPF

The Band Pass Filter filters the output of the LNA to the 144-148MHz
band to avoid aliasing in the AX5043 chips and to remove strong
signals that might affect RX.

### RF Splitter

The RF splitter takes the output of the BPF (at 50 ohms) and splits it
into four separate signals (at 50 ohms).  Each signal is about 6.5dB
lower than the input signal.

### AX5043

The AX5043 receivers take the RF from the splitter and receive AFSK
signals.  They may be configured to receive other FSK-type signals,
too.  The processor communicates with these over a SPI bus.

## TX

The board has one transmitter for sending FSK-type signals.  The main
transmission format is G3RUH, though it can dynamically switch to
other FSK modulation formats under software control.  It can transmit
at approximately 31dBm, though this can be reduced in the AX5043.  It
is designed for the 430-440MHz range.

### AX5043

The AX5043 receives data over SPI from the CPU for transmission.
There is some filtering done on the output of this.

### PA

The PA takes the signal from the AX5043 and amplifies it to up to
33dBm.

### LPF

The LPF on the output of the PA reduces output noise.  It's 3dB cutoff
is 460MHz.  It introduces ~2dB of loss, giving the maximum 31dBm power
output.

### Power Measurement

An optional power measurement circuit is provided using a directional
coupler on the board.  This can measure both forward and reflected
power.  It can be depopulated if not required.

## Dual Board Fault Tolerance

The board, as described in the design document, can operation in a
dual-board fault tolerant configuration.  Only one board can transmit
at a time.  These signals and switches allow two boards to control
each other and communicate so they can decide that one board is active
and the other is standby.  If a board fails, the other board can
detect this, take over operation, and power cycle the failed board to
hopefully bring it back up.

The MRAM software subsystem keeps the MRAMs on the boards in sync over
the CAN busses so the standby board can take over operation seamlessly
when it becomes active.

The boards are called "board1" and "board2".  A resistor on the board
tells the CPU which board it is.

This can also be configured so an external device can decide which
board is active and which is standby.

This entire section is optional and may be removed.  Bypass zero-ohm
resistors are supplied for the few lines that are required for
operation.

board2 does not have the RF portion (TX/RX Switch) of this populated
(or has it disabled and bypassed).  All TX/RX switching is done on
board1.

### TX Switch

The TX switch switches the TX antenna between board1 and board2.  It
uses the active line for board1 to do this.  The inactive board has
its TX output routed through a resistor to the RX side of the same
board; this can be used for loopback testing of the board, even in
simplex configurations if properly populated.

### RX Switch

The TX switch switches the TX antenna between board1 and board1.  It
uses the active line for board1 to do this.  The inactive board
receives the output of it's TX section through a resistor, as
described above.

# System Interfaces Description

This section defines the interfaces used to interact with the PacSat
AFSK board.

All connections to the CSKB connectors H1 and H2 can be moved to
different pins as required.

## Power

The board can run on just external +5V if configured with a 3.3V
regulator, or it can run on external +5V and +3.3V.  External power
interfaces have inductors to regulate surge at startup.

The default power pins are the ones defined by the ISIS ICEPS2 power
supply, and a zero-ohm resistor can choose either the man +5V/+3.3V
inputs, or one of the three secondary switched inputs, on the Cube Sat
Kit Bus interface.

A power disable, named HW\_POWER\_OFF1\_N, can be used to disable
power on the board.  If this is pulled low, all power zones but +5VAL
will be off.  This is pulled high on the board, so it does not have to
be driven.  This is part of the dual-board controls, but in a simplex
situation it can be used to externally control power on the board.

Power requirements are TBD.

## UMBILICAL\_ATTACHED

This signal tells the board that the satellite is in the launch
vehicle.  High (3V) means attached, ground means it's not in the
launch vehicle.  The processor can read this line, and if high it will
disable the RF PA so the board cannot transmit.

And optional pull-down on the line can be populated if the line is not
externally driven.  This must be low for the board to be able to
transmit.

## CAN Bus

The board has two CAN busses, CANA and CANB.  These are used for
external entities to supply control and telemetry and to send messages
to other entities from the board.

This interface is only capable of CAN 2.0, it cannot do CAN FD or CAN
XL.  A protocol design to do messaging over the 8-byte CAN 2.0
packets is described in a later section, CAN Bus Messages, along with
the messages themselves.

## I2C

An I2C bus is wired to the CSKB.  Termination is provided on the
PacSat board, though it could be removed if necessary.

The default pins for this are chosen as defined in "Standardization
Approaches for Efﬁcient Electrical Interfaces of CubeSats" at
https://www.researchgate.net/publication/354837502_Standardization_Approaches_for_Efficient_Electrical_Interfaces_of_CubeSats?enrichId=rgreq-3c8f3f7a94bf0ca750dcd71e69db6025-XXX&enrichSource=Y292ZXJQYWdlOzM1NDgzNzUwMjtBUzoxMDcxODgzMjE0NjYzNjgxQDE2MzI1NjgyODEyNzE%3D&el=1_x_2&_esc=publicationCoverPdf

## TX/RX connections

These connections provide antenna interfaces to the board.  The are 50
ohm U.FL connections.  It is expected that the connectors will be
epoxied down to the board.

On a simplex board, RX Antenna and TX Antenna provide separate
connections to a 144MHz receive antenna and a 440MHz transmit antenna.
The RX Board2 and TX Board2 connections are not used in this
configuration.

In a dual-board configuration, board 1 has the RX Antenna and TX
Antenna connection to the antennas.  The RX Board2 connection on board
1 is then wired to the RX Antenna connection on board2.  And the TX
Board2 connection on board 1 is then wired to the TX Antenna
connection on board2.  Board 1 will switch the external antenna
between the two boards depending on the value of the ACTIVE1\_N line.
See the design document for more details.

## Dual Board Controls

This is considered an internal interface between two PacSat boards,
used for fault tolerance.  Even though it runs over the CSKB
connector, it's not exactly and external interface, though it is
possible for an external entity to control the active/standby
configuration of the boards.  See the design document for details on
this.

Some of these, namely FAULT1\_N and PRESENCE1\_N, might be useful for
monitoring the board.  See the design document for details.

# Programming and Debug Interfaces

The board has two main interfaces for programming and debugging: A
JTAG interface and a serial port interface.

The JTAG is the primary programming interface, though capability to
program the device could be done over the serial port.

## JTAG

An ARM standard 10-pin JTAG header is provided on one edge of the
board, as described at
https://software-dl.ti.com/ccs/esd/documents/xdsdebugprobes/emu_jtag_connectors.html

To use the JTAG interface, the watchdog timer must be disabled or the
processor will be continuously reset.  A standard 2.54mm (.1") header
is provided at J4; when a jumper is installed the watchdog timer will be
disabled.

## Serial Port

A 3.3V serial port interface is provided on the edge of the board.
This is a standard 2.54mm (.1") header with three pins: TX, RX, and
ground.  Remember, when connecting to an external serial port, connect
TX to RX and RX to TX.

Only connect a 3.3V serial port interface.  Connecting a 5V or
standard RS-232 connection will likely damage the processor.
Connecting external TX to TX on the board will likely damage the
processor, and probably the external serial port, too.

## LP-XDS110 JTAG/Serial Debug Probe

TI sells the "XDS110 LaunchPad Debug Probe", part number LP-XDS110,
that is an inexpensive programming interface that can do both JTAG and
the serial port.

A separate ARM 10-pin JTAG cable (1.27mm pitch) will be required
(FIXME - find a reference for this, something like AdaFruit 1675 or
Sparkfun 15364) and jumper wires are require for wiring this in.

FIXME - Add pictures and diagrams for how to hook this up.

# Board Configuration

The PacSat board has a large number of configurations that can be
done.  See "Board Configuration" in the design document

# CAN Bus Messages

TBD
