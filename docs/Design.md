This document describes design and debugging information for the
PACSAT AFSK board.

Hooking Up JTAG and a serial port
=================================

The board uses a standard 10-pin 2x5 1.27mm pitch JTAG connector for a
debugger hookup.  The standard TI XDS110 debugger should work, though
I have not tried it.  I am using an LP-XDS110 from TI
(https://www.ti.com/tool/LP-XDS110).  You will need to get a cable,
since that doesn't come with the debugger board.  You can get one
at https://www.adafruit.com/product/1675
or https://www.digikey.com/en/products/detail/olimex-ltd/ARM-JTAG-20-10/3471401

Besides being a lot cheaper than the standard XDS110, the LP-XDS110
also has a serial port built in, so you don't have to have a separate
serial port interface.  Jumper J12 on the PacSat board is the serial
interface (3.3V) and the TX and RX lines are labeled under the pins.
The unlabeled pin is ground.  Remember, hook TX on one board to RX on
the other.  Don't hook TX to TX.  If you don't have the JTAG
connected, you will need to connect the ground as well.

The reset button on the LP-XDS110 resets the board.

The jumper on the LP-XDS110 decides which device powers the level
shifters.  If you are just using the serial port, the jumper should be
set to "XDS".  Otherwise the level shifters won't get power and they
won't work very well (you get erratic behavior).  If you have the JTAG
connector hooked up, the jumper should be set to "EXT" (or "TGT").
Otherwise the LP-XDS110 will be providing power to the device, which
you don't want.  In that case the PacSat board is powering the level
shifters.

Hooking Up Power
================

The normal board build only takes 5V.  There is a build option (or
some solder work) to remove the 3.3V regulator and supply 3.3V through
an external interface.

To hook up 5V, you can use jumper J5 (which is right by the PC104).
The 5V pin is labeled on the board.  Or you can use PC104 connector J2
(H2) pin 25 or 26 for 5V.

3.3V comes in jumper J6.  This could also be done from the PC104 J2
(H2) pin 27 or 28, but you would need to add resistor R111, which is
not installed by default.

There are also other pins on the PC104 which can supply 5V and 3.3V,
matching some power supplies, but certain resistors need to be
installed to do this.  They are not installed by default.

You obviously must hook up ground.  On the PC104 this is J2 (H2) pins
29, 30, and 32.  The other power pins have an associated ground.

Heat Sink for the Power Amplifier
=================================

The power amplifier has heat sink (or spreader) mounting on the bottom
of the board.  The PA is designed to transfer the heat that way,
according to the data sheet.

There is space and mounting holes for a 26mm by 12mm heat sink.
Mounting holes are M1.6 sized PTH centered 2.25mm from each edge.
The idea is to have a flat copper plat of that size.

The mounting hole centers are 21.5mm apart horizontally and 7.5mm
apart vertically.

Near the center of the plate there is a small block of copper to
extend down to the circuit board under the PA.  The PA has an open
copper area for this.  This area is 2.75mm x 2.75mm.  It's right edge
is located 14.10mm from the right side of the plate and the left edge
is located 9.16mm from the left side of the plate.  The top of the
area is 4.75mm from the top of the plate and 4.50mm from the bottom of
the plate.

It is unknown if the heat sink is required or what duty cycle on the
PA can be supported with and without it.  There is already a large
ground area on the bottom of the board for cooling.  But the provision
is there.  At worst case it needs to dissipate around 2W of heat. (The
PA is powered but no signal is transmitted.  When a signal is being
transmitted at full power, most of the power is being sent and only
around .5W is being dissipated by the PA.  It may also be possible to
reduce the quiescent current drawn by the PA by modifying the Iref
current.

It would also be possible to connect the top of the chip via some type
of riser to the shield to provide additional radiation surfaces for
the PA.

On Amazon you can search for "copper flat bar" to find suitable
material.  The PA is .85mm tall, the shield is 2.54mm, leaving 1.69mm
(.067") of space between the shield and the PA.  A 1/16" (.0625) will
probably work for a connection from the PA to the shield, though it
might be a tad too thick.  It could be sanded a bit.

You would probably want a 1/8" thick bar for the heat sink on the
bottom.  You could use a 2.75mm square piece of it to place on the PA
pad then put a 12mm x 26mm (.47" x 1") piece on top of that, drill 2mm
holes, and screw it down.  There's a little bit of slack on the large
piece dimensions, 1/2" width would be fine, adding a bit to the length
would be ok, too.

The board is ~1.6mm thick, 1/4" is 6.32mm, so that's 7.92mm.  You can
find M1.6 x 10mm stainless steel screws on Amazon along with nuts that
should work to fasten down the heat sink.  You would also need a space
grade thermal adhesive or paste.

RF Connections
==============

The Version 3 and later boards have an MMCX connector, P15 for
transmit and P17 for receive for connecting to the antennas.  The
receiver has significant filtering above 160MHz; you can transmit and
receive simultaneously with nearby antennas without issues.

There is a shared antenna input (P25) and associated diplexer that can
be used for a shared receive/transmit antenna, not installed by
default.  The parts on the diplexer page will need to be populated.
The RF input and RF output connectors can be removed in that case as
well as the bleed-off inductors on the RF input and output.  This
option costs about 1dB on both transmit and receive.

Version 3 boards also two U.FL connectors, P23 for transmit and P24
for receive (not populated by default), that can also be used for
antenna connections.  These could also be connected together to share
an antenna on one MMCX connector.

Version 2 boards have two U.FL connectors, P15 for transmit and P17
for receive, for antenna connections.

All boards have various U.FL connectors (not necessarily populated on
Version 3 and later boards) on the bottom of the board.  These are
mostly used for isolating and testing circuits.  However, they could
be used for bringing out or injecting signals.  For instance:

* If you wanted to be able to receive 160MHz or below on an external
  board, you could disable or remove one of the AX5043s and route it's
  RF splitter output to another board.  There are obvious places for
  doing this.

* If you wanted to bring in your own receive signal, there are obvious
  places for that.  This could be used, for instance, if you have an
  external downconverter to hook to the board and you didn't need the
  filtering and/or LNA.

* If you wanted to route the output of the AX5043, or the direct
  output of the PA, to another board.  This could be used for an
  external amplifier or and external upconverter.

RF Loopback Testing
===================

The Transmit AX5043 has an 18nH inductor installed for its PLL.  This
doesn't seem to affect ranging at 435MHz, but it allows it to range in
the 145MHz area, too.

You can use this to do a loopback test, transmit out in the 145MHz
area and receive there, too.  The receiver will pick up stray output
from the transmitter on the board, but the power will be very low.
(This was tested without shields, shields might eliminate that.)  When
going out the antenna port to a nearby antenna and then back in, the
power will be much stronger.

This should work through the diplexer, if that is installed, but you
can't test the actual antennas in that case.

With this, it is possible to test the entire RF chain.

Hardware Watchdog
=================

Jumper J4 disables the hardware watchdog when installed.  When
programming and debugging you need to install this jumper.

I2C
===

I2C can be run to the PC104.  These are on J1 (H1) pins 41 and 43,
which is semi-standard.

On version 3 and later boards, U32 and U38 must be installed (the
default) and then the PC104\_I2C\_EN\_N line must be enabled to turn
on access to this.  To permanently add a connection, U32 and U38 can
be removed and a 0402 zero-ohm resistor connected between pins 2 and 4
on both devices.

On version 2 boards, resistors R113 and R122 need to be installed.

CAN Bus
=======

Two CAN buses are routed to the PC104 and they are on by default.  CAN
A is on H1 (J1) pins 5 (the +) and 1 (the -).  CAN B is on H1 (J1)
pins 33 (the +) and 34 (the -).

These are not standard, except a NanoMind device specifies a CAN bus
on H2 pins 1 and 5.

CAN A can be disabled by removing U14 and R50 and R51.  CAN B can be
disabled by removing U22 and R89 and R90.

PC104 Serial Port
=================

The second serial port from the processor is run to PC104 J2 (H2) pins
22 (RX) and 21 (TX).

On version 3 and later boards, U39 and U40 must be installed (the
default) and then the PC104\_SER\_EN\_N line must be enabled to turn
on access to this.  To permanently add a connection, U39 and U40 can
be removed and a 0402 zero-ohm resistor connected between pins 2 and 4
on both devices.

On version 2 boards, You need to install R123 and R124 to make this
connection.  However, RX and TX are backwards so special jumpering on
R123 and R124 will be required to make it work.

Differences between the Version 2 and Version 3 board
=====================================================

* The ACTIVE\_N GPIO is now ACTIVE, changed to positive logic.

* The OTHER\_FAULT\_N GPIO is now OTHER\_FAULT, changed to positive
  logic.

* The OTHER\_HW\_POWER\_OFF\_N GPIO is changed to
  OTHER\_HW\_POWER\_ST.  It is now positive logic, and the name has
  been changed to reflect that it is measuring the other power off
  state.

* OTHER\_ACTIVE\_N has changed to positive logic, OTHER\_ACTIVE now.

* A DAC has been added to the AX5043 SPI bus to control the quiescent
  current into the PA.  This should allow the power usage of the PA to
  be directly controlled.  There is also a uninstalled resistor that
  can be installed (and the DAC removed) as a build option.

* The serial RX and TX lines on the PC104 were backwards on the
  version 2 board.  They are fixed on the version 3 board.

* Unfortunately, CAN A was moved on the PC104 from pins 23 (+) and 24
  (-) to pins 5 (+) and 1 (-).  This matches the NanoMind
  configuration, which is the only thing I found with a CAN bus.  Pins
  23 and 24 are already used on the power supply for ground and
  alternate I2C, so they could not be used for CAN.

* PC104\_I2C\_EN\_N and PC104\_SER\_EN\_N for connecting the I2C and
  serial lines to the PC104.
  
* There is a thermsistor added by the oscillator for frequency tuning,
  and for general power measurement.  This goes into AD1IN[09].

IO Connections on the PacSat AFSK processor
===========================================

These are the pins on the TMS570 processor, where they go, what they
do and some notes at the end with some more details.

The "G" column shows the GPIO usage and capability.  The first letter
is how the GPIO is used: I for input, O for output, B for
bidirectional, blank if not used as a GPIO, and ? if the function is
not known (the PC104 pins).  The second letter is U for pullup by
default and D for pulldown by default or blank if the pin cannot be
used as a GPIO.

|Pin3	|CPU Pin Name			|Schematic Name			|G |Description |
|----	|------------			|--------------			|--|----------- |
|1		|GIOB[3]				|OTHER\_FAULT			|ID|Fault line from other board |
|2		|GIOA[0]				|						| D|free gpio|
|3		|MIBSPI3NCS[3]			|I2C\_SCL				|OU|RTC control (MAX31331TETB+) |
|4		|MIBSPI3NCS[2]			|I2C\_SDA				|BU|RTC control (MAX31331TETB+) |
|5		|GIOA[1]				|AX5043\_IRQ\_RX1		|ID|Interrupt from AX5043 RX1 |
|6		|N2HET1[11]				|OTHER\_HW\_POWER\_ST   |ID|Power off state for the other board |
|7		|FLTP1					|						|  | |
|8		|FLTP2					|						|  | |
|9		|GIOA[2]				|OTHER\_PRESENCE\_N		|ID|Presence line from other board |
|10		|VCCIO					|						|  | |
|11		|VSS					|						|  | |
|12		|CAN3RX					|CAN\_A\_RX				|IU|CAN bus transceiver |
|13		|CAN3TX					|CAN\_A\_TX				|OU|CAN bus transceiver |
|14		|GIOA[5]				|AX5043\_IRQ\_RX4		|ID|Interrupt from AX5043 RX4 |
|15		|N2HET1[22]				|						| D|free gpio|
|16		|GIOA[6]				|OTHER\_ACTIVE			|ID|Active line from other board |
|17		|VCC					|						|  | |
|18		|OSCIN					|						|  | |
|19		|Kelvin\_GND			|						|  | |
|20		|OSCOUT					|						|  | |
|21		|VSS					|						|  | |
|22		|GIOA[7]				|AX5043\_IRQ\_RX3		|ID|Interrupt from AX5043 RX3 |
|23		|N2HET1[01]				|						|OD|Yellow LED |
|24		|N2HET1[03]				|AX5043\_EN\_RX4\_N		|OD|Power enable for AX5043 RX 4 |
|25		|N2HET1[00]				|						|OD|Red LED |
|26		|VCCIO					|						|  | |
|27		|VSS					|						|  | |
|28		|VSS					|						|  | |
|29		|VCC					|						|  | |
|30		|N2HET1[02]				|						|OD|Green LED |
|31		|N2HET1[05]				|LNA\_ENABLE			|OD|Used to enable the LNA |
|32		|MIBSPI5NCS[0]			|						| U|free gpio (Save for extra SPI if possible) |
|33		|N2HET1[07]				|AX5043\_EN\_RX3\_N		|OD|Power enable for AX5043 RX 3 |
|34		|TEST					|					    |  | |
|35		|N2HET1[09]				|AX5043\_EN\_RX2\_N		|OD|Power enable for AX5043 RX 2 |
|36		|N2HET1[04]				|AX5043\_EN\_RX1\_N		|OD|Power enable for AX5043 RX 1 |
||||||
|37		|MIBSPI3NCS[1]			|MRAM\_NCS3				|OU| |
|38		|N2HET1[06]				|UART\_RX1				|ID|PC104 pin 92 |
|39		|N2HET1[13]				|UART\_TX1				|OD|PC104 pin 88 |
|40		|MIBSPI1NCS[2]			|MRAM\_NCS2				|OU| |
|41		|N2HET1[15]				|CAN\_A\_EN\_N			|OD|CAN bus A transceiver enable |
|42		|VCCIO					|						|  | |
|43		|VSS					|						|  | |
|44		|VSS					|						|  | |
|45		|VCC					|						|  | |
|46		|nPORRST				|						|  | |
|47		|VSS					|						|  | |
|48		|VCC					|						|  | |
|49		|VCC					|						|  | |
|50		|VSS					|						|  | |
|51		|MIBSPI3SOMI			|MRAM\_MISO				|IU| |
|52		|MIBSPI3SIMO			|MRAM\_MOSI				|OU| |
|53		|MIBSPI3CLK				|MRAM\_CLK				|OU| |
|54		|MIBSPI3NENA			|MRAM\_NCS1				|OU| |
|55		|MIBSPI3NCS[0]			|MRAM\_NCS0				|OU| |
|56		|VSS					|						|  | |
|57		|VCC					|						|  | |
|58		|AD1IN[16] / AD2IN[0]	|\*						|  |Thermsistor near the processor |
|59		|AD1IN[17] / AD2IN[01]	|						|  |Board Number |
|60		|AD1IN[0]				|						|  |free adc |
|61		|AD1IN[07]				|PWR\_FLAG\_AX5043		|  |Power flag from the AX5043 current limiter |
|62		|AD1IN[18] / AD2IN[02]	|						|  |External Control |
|63		|AD1IN[19] / AD2IN[03]	|						|  |free adc |
|64		|AD1IN[20] / AD2IN[04]	|VER\_BIT0				|  |Board version number bit 0 |
|65		|AD1IN[21] / AD2IN[05]	|VER\_BIT1				|  |Board version number bit 1 |
|66		|ADREFHI				|						|  | |
|67		|ADREFLO				|						|  | |
|68		|VSSAD					|						|  | |
|69		|VCCAD					|						|  | |
|70		|AD1IN[09] / AD2IN[09]	|						|  |Thermsistor by the oscillator |
|71		|AD1IN[01]				|VBATT					|  |Voltage from the battery rail |
|72		|AD1IN[10] / AD2IN[10]	|PWR\_FLAG\_5VAL		|  |Power flag from the +5VAL current limiter |
||||||
|73		|AD1IN[02]				|REV\_PWR				|  |\*Reverse RF TX Power |
|74		|AD1IN[03]				|FWD\_PWR				|  |\*Forward RF TX Power |
|75		|AD1IN[11] / AD2IN[11]	|PWR\_FLAG\_LNA			|  |Power flag from the LNA current limiter |
|76		|AD1IN[04]				|PWR\_FLAG\_SSPA		|  |Power flag from the PA current limiter |
|77		|AD1IN[12] / AD2IN[12]	|						|  |+5V power measure, linear from 0-2.5V |
|78		|AD1IN[05]				|						|  |free adc |
|79		|AD1IN[13] / AD2IN[13]	|						|  |+1.2V power measure, 0-1.2V |
|80		|AD1IN[06]				|						|  |+3.3V power measure, 0-1.65V |
|81		|AD1IN[22] / AD2IN[06]	|						|  |free adc |
|82		|AD1IN[14] / AD2IN[14]	|						|  | Board version number bit 2 |
|83		|AD1IN[08] / AD2IN[08]	|\*POWER\_TEMP			|  |Thermsistor in power conversion section |
|84		|AD1IN[23] / AD2IN[07]	|\*PA\_TEMP				|  |Thermsistor near the PA |
|85		|AD1IN[15] / AD2IN[15]	|						|  |Board version number bit 3 |
|86		|AD1EVT					|						| D|free gpio |
|87		|VCC					|						|  | |
|88		|VSS					|						|  | |
|89		|CAN1TX					|AX5043\_EN\_TX\_N		|OU|Power enable for AX5043 TX |
|90		|CAN1RX					|AX5043\_SEL1\_N		|OU|SPI chip select for AX5043 RX1 |
|91		|N2HET1[24]				|AX5043\_SEL2\_N		|OD|SPI chip select for AX5043 RX2 |
|92		|N2HET1[26]				|AX5043\_SEL3\_N		|OD|SPI chip select for AX5043 RX3 |
|93		|MIBSPI1SIMO			|AX5043\_MOSI			|IU|SPI MOSI for all AX5043s |
|94		|MIBSPI1SOMI			|AX5043\_SIMO			|OU|SPI SIMO for all AX5043s |
|95		|MIBSPI1CLK				|AX5043\_CLK			|OU|SPI clock for all AX5043s |
|96		|MIBSPI1NENA			|AX5043\_SEL4\_N		|OU|SPI chip select for AX5043 RX4 |
|97		|MIBSPI5NENA			|AX5043\_SEL\_TX\_N		|OU|SPI chip select for AX5043 TX |
|98		|MIBSPI5SOMI[0]			|						| U|free gpio (Save for extra SPI if possible) |
|99		|MIBSPI5SIMO[0]			|						| U|free gpio (Save for extra SPI if possible) |
|100	|MIBSPI5CLK				|						| U|free gpio (Save for extra SPI if possible) |
|101	|VCC					|						|  | |
|102	|VSS					|						|  | |
|103	|VSS					|						|  | |
|104	|VCCIO					|						|  | |
|105	|MIBSPI1NCS[0]			|CAN\_B\_EN\_N			|OU|CAN bus B transceiver enable |
|106	|N2HET1[08]				|						| D|free gpio|
|107	|N2HET1[28]				|PA\_DAC\_SEL\_N		|OD|Select pin for the PA DAC Iref, on the AC5043 SPI bus |
|108	|TMS					|JTAG pin				|  | |
||||||
|109	|TRST					|JTAG pin				|  | |
|110	|TDI					|JTAG pin				|  | |
|111	|TDO					|JTAG pin				|  | |
|112	|TCK					|JTAG pin				|  | |
|113	|TCK					|JTAG pin				|  | |
|114	|VCC					|						|  | |
|115	|VSS					|						|  | |
|116	|nRST					|\*Processor\_Reset		|  |Main reset pin for the processor |
|117	|nERROR					|FAULT\_N				|  |Output ERROR line from the processor |
|118	|N2HET1[10]				|OTHER\_HW\_POWER\_OFF  |OD|Power off the other board |
|119	|ECLK					|UMBILICAL\_ATTACHED	|ID|PC104 pin |
|120	|VCCIO					|						|  | |
|121	|VSS					|						|  | |
|122	|VSS					|						|  | |
|123	|VCC					|						|  | |
|124	|H2HET1[12]				|POW\_MEAS\_EN			|OD|\*TX power measurement enable |
|125	|H2HET1[14]				|PA\_PWR\_ON			|OD|Enable PA power |
|126	|GIOB[0]				|AX5043\_IRQ\_RX2		|ID|Interrupt from AX5043 RX2 |
|127	|N2HET1[30]				|PC104\_SER\_EN\_N		|OD|Connect the 2nd serial port to the PC104|
|128	|CAN2TX					|CAN\_B\_TX				|OU|CAN bus B transmit |
|129	|CAN2RX					|CAN\_B\_RX				|IU|CAN bus B receive |
|130	|MIBSPI1NCS[1]			|\*FEED\_WATCHDOG		|OU|Resets the hardware watchdog timer |
|131	|LINRX					|PC104\_RX				|IU|PC104 Pin H2-21 |
|132	|LINTX					|PC104\_TX				|OU|PC104 Pin H2-22 |
|133	|GIOB[1]				|ACTIVE					|BD|Local active pin for active/standby |
|134	|VCCP					|						|  | |
|135	|VSS					|						|  | |
|136	|VCCIO					|						|  | |
|137	|VCC					|						|  | |
|138	|VSS					|						|  | |
|139	|N2HET1[16]				|PC104\_I2C\_EN\_N		|OD|Connect the I2C bus to the PC104|
|140	|N2HET1[18]				|PC104\_ABF0			|ID|PC104 pin H2-50|
|141	|N2HET1[20]				|AX5043\_PWR\_EN		|OD|Main power enable for all AX5043s |
|142	|GIOB[2]				|AX5043\_IRQ\_TX		|ID|Interrupt from AX5043 TX |
|143	|VCC					|						|  | |
|144	|VSS					|						|  | |


\*Notes below

Interrupts and GPIOs
--------------------

On the TMS570, most normal pins can also be used at GPIOs, but they
are not capable of generating interrupts.  Only the GIOx[n] pins can
generate interrupts, and they are all used for that purpose.


Notes on thermsistors
---------------------

Thermsistors are connected to ADC pins on the processor to measure
temperatures on the board.  Resistance varies from 534 ohms (125C) to
188.5K (-40C).  There is a 10K bias, so this gives this gives a .17V
(125C) to 3.13V (-40C) voltage range.  It is supposed to be fairly
linear, but does require compensation by software.

Notes on Processor\_Reset
------------------------

The 3.3V and 1.2V power converts have power good output pins, and the
1.2V current limiter has a power good pin, all open collector.  These
are wire-or-ed to the processor reset pin.  When any of them senses
there is a power issue, they will pull the reset pin.  After the 1.2V
current limiter turns on (which takes a little bit of time, it is
inrush limited) it will wait 50us and before releasing the reset pin,
so reset should happen automatically on any power up or power problem.

Notes on FEED\_WATCHDOG
-----------------------

This must be toggled at least once a second.  If it isn't, the
hardware watchdog will power off the board for 200ms and power it back
on.

Notes on TX Power Measurement
-----------------------------

A directional coupler and power measurement chips (ADL5501AK) feed
into the ADCs (Forward power to pin 74 AD1IN[3] and reverse to pin 73
AS1IN[2]) and an enable for those parts into pin 124 N2HET1[12].  Pin
124 is pulled down by default, so the chips will be disabled at reset.
The direction coupler is 4mm long with .1524mm traces .127mm apart.
At full power out (+33dBm) this will result in about -7dBm of power
from the coupler.  This was simulated with a transmission line in
qucs.  The voltage for that can be calculated from the chip manual.

Other IO Connections
====================

WATCHDOG\_OUT\_N
----------------

A line is run from the hardware watchdog output to the RTC DIN input.
That input can be set up to measure transitions and store the
information.  This way the process can tell if the reset came from the
hardware watchdog.  The watchdog is negative logic, so a transition
from high to low will say that the hardware watchdog was triggered.

PC104 Pins
==========

FIXME - Figure out what all the PC104 pins do.

These pins handle active-standby between to PacSat AFSK board and
various signals from the control board of the satellite.

  - HW\_POWER\_OFF[12]\_N - Input to board, pulling this low causes the
    power to be disabled on boardn.  boardn pulls this high with a 10K
	resistor.  If driven, it should be open drain or open collector.
	Be careful not to glitch this line.

  - PRESENCE[12]\_N - The board is physically present.  This must be
	pulled high by a 1M resistor on entity reading this value, it is
	pulled low by a 10K resistor on boardn.
	
  - ACTIVE[12]\_N - boardn is asserting that it is active.  This is
	pulled high on boardn and will be driven low by boardn when it is
	active and not under external active/standby control.  When under
	external active/standby control, this is an input that another
	entity must pull low to cause the board to go active.
	
  - FAULT[12] - Output from boardn, the processor is reporting an error.
    Positive logic (high is fault).

  - UMBILICAL\_ATTACHED - Input to the board, if high the satellite is in
    the launch vehicle.  This inhibits transmit in hardware and causes
	the software to behave differently.  If this line is not used make
	sure to populate the resistor pulling it down.
	
  - SAFE\_MODE\_N - Connected to the processor so a controlling system
    can tell it to go into a safe mode.  What it does depends on context.

  - 5V_p - +5V that is always present when the satellite is powered.
    The board has a 0 ohm resistor that must be populated to get power
	from these pins.

  - 3V3_p - +3.3V that is always present when the satellite is powered.
    The board has a 0 ohm resistor that must be populated to get power
	from these pins.

  - 5V_S[1-3] - Switched +5V power from the power supply.  The board
    has 0 ohm resistors, one of which must be populated to get power
    from these pins.

  - 3V3_S[1-3] - Switched +3.3V power from the power supply.    The
	board has a 0 ohm resistor that must be populated to get power
	from these pins.

  - I2C\_SDA, I2C\_SCL - I2C bus pins

  - GND

  - CAN[AB][+-] - CAN bus signals.

Power Control and Sequencing
============================

The power control on the board is fairly simple.  On power up, power
comes in through VSYS, goes through and inductor, and goes to +5V,
which is always powered on.  +5V goes through a current limiter to
+5VAL, which power the circuits on the board that are always on, the
circuits the handle the board presence/active/etc. and the board1 RF
switches, and the CAN bus transceivers.  3.3V comes in to REG\_3V3
from the bus.

The TPSM828302ARDSR will start supplying 1.2V to REG\_1V2.  It will
also pull the PROCESSOR\_RESET pin low until their power is good, and
that point they will not pull the reset line low any more (they are
open drain).  At that point the MP5073GG-P is also holding reset line
low until it is enabled.  Since the MP5073GG-P is powered by REG\_3V3
it will not let the reset line go until that power is good.

The STWD100NYWY3F hardware watchdog will power up at that time, but
the POWER\_ENABLE pin from it will be pulled high and should remain
high for 1 second.

The MP5073GG-P and MAX4495AAUT current limiting chips will start
supplying power to the rest of the board once they detect that power
is good.  However, the MP5073GG-P will wait 50us after it senses the
1.2V power is good holding the PROCESSOR\_RESET line low, then it will
let the processor go.

All the chips driving the PROCESSOR\_RESET line have power sensors, if
any of them sense that the power is bad they will pull that line down
low.

When the processor is in reset and the default settings on the
PA\_PWR\_EN, AX5043\_PWR\_EN, and LNA\_ENABLE are pulled low (and
they have pull downs, too, so that they are disabled even when the
main power is disabled), so all power to the RF elements will be
off.

A HW\_POWER\_OFF\_N comes in from the PC104 connector; if that is
pulled low it will power off everything on the board except for the
devices on +5VAL.  It does this by disabling the 3.3V and 1.2V
regulators.  When 3.3V is off, the MAX4995s controlling power to the
PA, AX5043s, and LNA will be powered off.

There is also a hardware watchdog, as mentioned before.  The processor
must toggle the FEED\_WATCHDOG line at least once a second.  If it
fails to do that, the 1.2V and 3.3V current limiters will be disabled
cutting power to the processor and all digital components.  This will
result in everything else being powered off (except the devices on
+5VAL).  After 200ms, the watchdog chip will enable power again.

To power up and enable the RF section, the processor must first make
sure all the AX5043 enable lines are pulled high to disable them.
This is not the default (some are low and some are high by default),
but it doesn't matter because they are powered off at the main,
anyway.  The processor then can drive AX5043\_PWR\_EN high to enable
the power to all AX5043s.  The processor can then drive the individual
AX5043 enables low to individually power them on.  Then the processor
can drive PA\_PWR\_EN high to power on the PA and LNA\_ENABLE high
to power on the LNA.

Board Configuration
===================

The board has a number of resistors and optional parts for
configuration.  These are:

  - 1.2V\_INPUT - Determines whether 1.2V is derived from 3.3V or 5V.

  - BOARD\_NUM - Remove for board 1 or simplex, populate for board 2.

  - EXTERN\_CONTROL - Remove if the board (or board pair) manage their
    own activity and power state.  Populate if another entity controls
    power and the active lines on a board pair.  This should generally
    not be populated on a simplex board, it will always be active and
    some other entity probably controls its power signal.
	
  - 5V\_S[1-3], 5V\_p - One of these should be populated depending on
    where the board should get its +5V power.

  - 3V3\_S[1-3], 3V3\_p - One of these should be populated depending on
    where the board should get its +3.3V power.  In addition, there is
	an optional buck regulator that can be populated to derive 3.3V
	from 5V.

  - RF\_SWITCH\_EN - Removing the resistor to +5AL will disable all
    the RF switches into high impedance mode.  Then the zero ohm
    resistors to bypass the switches can be added.

  - UMIBLICAL\_ATTACHED - If this line is not externally used, the
    resistor from this to ground must be populated.

In addition, for simplex, or if each board in a two-board set has its
own antenna connections or antennas, all the chips and resistors on
the RF Output Switch and RF Input Switch schematic pages can be
removed, the zero-ohm resistor between RF\_OUT\_SWITCH and "TX ANT
OUT" can be added, and the zero-ohm resistor between RF\_IN\_SWITCH
and "RX ANT IN" be added to remove all the RF switching.

To completely remove active-standby, in addition to the previous
paragraph, all the parts and resistor and the Active Standby Config
page can be removed and the zero-ohm resistor between
HW\_POWER\_OFF1\_N and HW\_POWER\_OFF\_N added for external power
control of the board.

The power output measurement circuitry on the RF\_Power\_AMP\_FET page
can be removed if output or reflected power measurements are not
necessary.

Active/Standby
==============

The boards supports having a mate board that is the same board with
one resistor difference to differentiate between board 1 and board 2.
The BOARD\_NUM line is used to tell which board you are.  This also
selects values coming from the PC104.  The "other" board is the board
you are not.

PC104 Interface
---------------

The lines on the PC104 are:

- PRESENCEn\_N - This is used to tell if the other board is present
  (even if it is powered down).  It will be high if not present and
  low if present.

- FAULTn - This is used to tell if the other board has had a fault
  and is failing.  This board can take over processing at that point.

- ACTIVEn\_N - Used to tell which board is active.  The board that is
  asserting its line thinks it is active.  If both boards assert this,
  board 1 will be active and board 2 must deactivate.

- HW\_POWER\_OFFn\_N - Used to power the other board off.  It this
  board thinks the other board is misbehaving, it can power off the
  other board.

The lines from the other board become OTHER\_PRESENCE\_N,
OTHER\_FAULT, OTHER\_ACTIVE, and OTHER\_HW\_POWER\_OFF on a
board.  The lines for this board become PRESENCE\_N, FAULT,
ACTIVE, and HW\_POWER\_OFF\_N.

The active board may also be externally controlled.  If the
EXTERN\_CONTROL line is pulled high, the board will assume that some
other external entity will choose which board is active.  In this
case, the ACTIVE\_N line becomes an input and the processor monitors
that line to know if it should be active or not.

The ACTIVE1\_N line also controls several RF switches on board 1.
There is a second set of SMA connectors that connect from board 1 to
board 2 to carry the RF to board 2.  If board 1 is active, the RF is
switched to board 1 and the RF to/from board 2 is not active (tied to
50 ohms in the QPC8010Q part).

On board 2, the RF switches are not populated (or are disabled) and
the RF goes through a zero ohm resistor to connect it, bypassing the
switch connections.  On board 1 these resistors must not be populated.
If the board is configured for simplex, then the RF switches are also
not populated or are disabled and the zero ohm resistors are populated.

It is also possible to have separate antennas for each board.  Then
the RF switches and second set of SMAs are not relevant and can be
removed.

All the board switch circuitry is powered with +5V so it works even if
the board is powered down.  Care must be taken to not drive any I/O
lines with +5V; voltage dividers are present in several places to
bring +5V down to +2.5V for pull ups.

See the end of this document for the active/standby state machine.

MRAM data is automatically synced to the other board via the CAN bus.
The inactive side has the MRAM unmounted and is only syncing data.
The sync protocol is reliable and the remote end must respond that it
has written the data before the local end commits the write.  When a
board activates, it mounts MRAM and continues operation.  Applications
can either store all state data in MRAM or they can implement their
own synchronization protocol.

When the other board is down and then comes up, it will request a full
sync and all data will be transferred.  On a requested activity
switch, special handling is done to keep both sides in sync so the
newly inactive side can simply start receiving updates and a full sync
is not required.

If the inactive board detects a sync error, it will request a full
sync.

The inactive board will have all RF powered down and will do minimal
processing to avoid using very much power.  Basically just handling
synchronization data.

Active/Standby State Machine
----------------------------

The logic below is for the board being active or not.  For instance,
if OTHER\_FAULT is low, then it is true.  These are all this way
since they are all negative logic.  This is only used if the active
state is not externally controlled.

The boards will switch activity periodically to test the other board.

  - PowerUp:

    - !OTHER\_PRESENCE\_N -> ActiveOtherBoardNotPresent
    - OTHER\_PRESENCE\_N && OTHER\_ACTIVE -> Inactive
    - OTHER\_PRESENCE\_N && !OTHER\_ACTIVE && !IAmBoard2 -> ActiveOtherBoardPresent
    - OTHER\_PRESENCE\_N && !OTHER\_ACTIVE && IAmBoard2 -> InactiveWaitActivate
      - start timer

  - Inactive:
    - OTHER\_FAULT -> ActiveOtherBoardPresent
      - power cycle other board.
    - !OTHER\_ACTIVE -> ActiveOtherBoardPresent
    - !OTHER\_PRESENCE\_N -> ActiveOtherBoardNotPresent
      - log presence issue

  - InactiveWaitActivate:
    - OTHER\_FAULT -> ActiveOtherBoardPresent
      - stop timer
      - power cycle other board.
    - OTHER\_ACTIVE -> Inactive
      - stop timer
    - !OTHER\_ACTIVE && timeout -> ActiveOtherBoardPresent
    - !OTHER\_PRESENCE\_N -> ActiveOtherBoardNotPresent
      - stop timer
      - log presence issue

  - ActiveOtherBoardPresent:
    - OTHER\_FAULT -> ActiveOtherBoardPresent
      - power cycle other board.
    - OTHER\_ACTIVE -> Inactive
    - !OTHER\_PRESENCE\_N -> ActiveOtherBoardNotPresent
      - log presence issue

  - ActiveOtherBoardNotPresent:
    - OTHER\_PRESENCE\_N -> ActiveOtherBoardPresent
      - log presence issue

Note that except for power up, transitions based on OTHER\_PRESENCE\_N
should never happen.  These should be logged.

FIXME - There needs to be some synchronization handling added to this.

FIXME - Some sort of handling needs to be added in the case that the
other board is determined to be faulty.

FIXME - May need to debounce some of these lines.

FIXME - For a controlled activity switch, it probably needs to be
handled by messaging and the hardware lines are used to do the final
switch.
