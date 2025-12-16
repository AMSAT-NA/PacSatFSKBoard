# New Board Bring up

Things to do for a new board:

* Add power connector.

* Add watchdog jumper.

* Replace RX AX5043 inductors.  18nH works well.

* Add blue wire for the LNA bias from between R77 and C105 to
  between L32 and C107/108.

* Replace U5 with the proper part.

* Possibly replace R117 with a 15/18K resistor.  The voltage is
  a little low for the AND gate input.  (Testing shows this is
  not necessary, so this doesn't have to be done on prototype
  boards.)

* Break the trace between L35 and C112 and add a 1nF capacitor there.
  This blocks DC to the PA input, as required by the chip.  The
  capacitor can be added between L35 and the PA, but that's a lot
  harder to do.  If the blocking capacitor is between L35 and C112
  that means you can't effectively use the TX\_PA\_DRV UFL connector
  (P13) because possibly there will be a DC path to ground through the
  UFL connector.  So you can only use TX\_PA\_DRV on boards with the
  capacitor between L35 and the PA.

* Change the PA power input inductor (L37) to a 100nH part to avoid
  feedback through the power supply.

* C117 was miscalculated.  It should (in combination with C123) be
  about 60pf.  Replace with a 68pF cap for now (giving about 64pF when
  combined with 1nF).  Ideally C117 should be 63pF to combine with C123
  to give 60pF.

# Current Board Status

## Board 5 - 2nd board I worked on

* Applied all the board bring up changes.

* It's working well, except for RF transmit power.

* This board has the capacitor on the PA RF input added between
  the L35 inductor and the PA, so the TX\_PA\_DRV input/output
  connector (P13) can be used on this board.

* The PA power input inductor (L37) has been changed to 100nH.

* U.FL connector P6 got pulled off the board.

* Currently C124, L30, C125, L33 and L38 are not installed.  I pulled
  them off to measure power out of the PA, and they are pretty much
  destroyed.  L33 and L38 came off when I was unsoldering the other
  devices.
  
## Board 6 - First board I worked on for initial bringup

* The RF switches have been removed and jumpers places on the RF connections.
  So this is basically a stand-alone board or a board 2.

* The board 2 resistor has not been added, but should be at some point.

* Added a 1nF capacitor between L35 and the RF PA so it's not DC grounded.

* The board usually goes into a reset loop when cold.  It started
  doing this after I put too much voltage in.  This is probably a
  power issue someplace.  Fixing the PA power controller did seem to
  help.  To get it out, you have to let the board warm up a little
  then bring the voltage down and back up until it works.

* The board draws a lot more power than it should.  Something in the
  power section got messed up, it appears.
  
* MITSI replaced the PA with a new chip because the old one was broken.

* The PA power input inductor (L37) has been changed to 100nH.

* PA output match capacitor (C117) was changed to 68pF.

* C112 between the AX5043 and the PA is currently removed for testing.

* L35 was broken off in the process of removing C112 and need to be
  replaced.  There's a 15nH one there for now.

## Board 8 - 3rd board I worked on

* Applied all the board bring up changes.

* It's working well, except for RF transmit power.

* Added the 1nF capacitor between L35 and C112, so TX\_PA\_DRV cannot
  be used on this board. (Well, not true any more.)

* The Iref input is modified to match what the datasheet says it
  should be.  Except the 68nH inductor got lost, so I put on an 83nH
  inductor, but that shouldn't matter.  It has Iref going to the
  inductor, then the 240ohm resistor, and the 0.1uF capacitor from above
  the inductor to ground.

* Change the L match on the PA input to a 47pf capacitor and a 15nH
  inductor.  This seems to work ok, though per simulation it has more
  loss than the two inductor L match.  This does make TX\_PA\_DRV
  usable.

* The PA power input inductor (L37) has been changed to 100nH.

### Fixed

* The RF power output switch U33 appears to always be connected from
  RF\_OUT\_SWTICH to the antenna output, no matter the setting of
  ACTIVE1\_N.  It's not that way on board 5, so it appears to be the
  switch.  I'm wondering if an over voltage messed it up?  Or maybe
  transmitted power?  But maybe it's working.  If I have a signal
  going out, turning the switch on and off give a 35dB difference in
  power.  This appears to not be an issue.

