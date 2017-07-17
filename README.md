Playing with CAN
================

_This was the subject of my presentation of this year's LSEWeek. Slides (english)
will soon be available, along with the stream of the presentation (french)_

## Sum up

I was curious about learning what makes a car. As time went by, I started
taking a look at cars internal systems, and finally ended up playing with CAN.
This repo is all of what I understood, read, wrote, and experienced with.

The repo is split in different parts:
- can_logs: Different CAN output while testing different things on
            different vehicles
- canpad: FaaG (Fiat as a Gamepad) - Play video games with your Fiat 500
- docs: PDFs and documentation I used during my analysis
- notes: Written notes and sum ups on different subjects (OBD, CAN, environement setup, ...)
- scripts: python-can scripts to play with the CAN bus

Tools and cars used:
- PiCan2
- VW Polo (6R, 6C) 1.2 (2009-..., 60 CH)
- Fiat 500c 69ch (2010)
- Lancia Voyager (2014)

## CANPad

CANPad allows one to pilot in video games by using real cars via CAN.
This repo contains two versions:
- v1: Creates a virtual controller via libuinput to control simple games that
      don't require real controllers (like VDrift). Tested on ArchLinux with
      VDrift.
      Demonstration video available [here](https://www.youtube.com/watch?v=-q2togYPXas)
- v2: Allows one to play more interesting games (like Dirt Showdown) on Linux
      by hijacking a real XBox like controller. Tested on ArchLinux with Dirt
      Showdown (Steam version) with an official XBox controller.
      Demonstration video available [here](https://www.youtube.com/watch?v=bB7m7J3ioQw)

Some codes are manufacturer specific (brakes pedal, clutch, steering wheel,
handbrake) and thus will only work with Fiat cars (maybe even Fiat 500 only,
maybe even Fiat 500c 2010 only, etc, I don't know). Feel free to try this on
different cars, and submit via pull requests new versions of CANPad!)

## "notes" disclaimer

These notes are a sum up of what can be found on the internet or in the
various documents presents in ../docs.
Everything comes from my understanding of what I read and thus must be taken
with care, since mistakes can be (and have been) made during these researches.

For any question, feel free to send me an email at p1kachu@lse.epita.fr

## Other links

- https://hackaday.io/project/6288/logs
- http://jazdw.net/tp20
- https://hackaday.io/project/6288-volkswagen-can-bus-gaming
- http://illmatics.com/carhacking.html
- http://nefariousmotorsports.com/forum/
- http://nefariousmotorsports.com/forum/index.php?topic=4983
- http://www.ti.com/lit/an/sloa101b/sloa101b.pdf
- See 'notes' for more
