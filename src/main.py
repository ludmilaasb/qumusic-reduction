import struct
from io import BytesIO

fn = "ABBUC_20_1_(subsong 0).mid"

# MThd <length><format><ntrks><division>

def read_uint32(handle):
    return struct.unpack(">L", handle.read(4))[0]

def read_uint16(handle):
    return struct.unpack(">H", handle.read(2))[0]

def read_uint8(handle):
    return struct.unpack("B", handle.read(1))[0]

def read_int8(handle):
    return struct.unpack("b", handle.read(1))[0]

def read_string(handle, length):
    return handle.read(length).decode('ascii')

def readVarLen(handle):
	value = struct.unpack("B",handle.read(1))[0]
	if value & 0x80:
		value = value & 0x7F
		c = struct.unpack("B",handle.read(1))[0]
		value = (value << 7) + c & 0x7F
	return value

def note_name(k):
    return ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"][k % 12] + str(k // 12 - 1)

with open(fn, "rb") as midi:
    midi.seek(0, 2)
    midisize = midi.tell()
    midi.seek(0)
    print("Midi size: %d bytes" % midisize)
    
    print(read_string(midi,4))
    msize = read_uint32(midi)
    print(msize)
    mformat = read_uint16(midi)
    print(mformat)
    ntracks = read_uint16(midi)
    print(ntracks)
    mtimebase = read_uint16(midi)
    print(mtimebase)

    while midi.tell() < midisize:
        header = read_string(midi,4)
        if header == "MTrk":
            print("----- Track start -----")
            tsize = read_uint32(midi)
            tdata = BytesIO(midi.read(tsize))
            reading_track = True
            while reading_track:
                delta = readVarLen(tdata)
                print("\nDelta: %d ticks" % delta)
                msgtype = read_uint8(tdata)
                print("Message type: {:02X}".format(msgtype))
                if msgtype == 0xFF: # Meta event
                    evtype = read_uint8(tdata)
                    print("Event type: {:02X}".format(evtype))
                    if evtype == 0x7F: # Sequencer Specific
                        size = readVarLen(tdata)
                        tdata.read(size)
                        print("Skipped %d bytes (Sequencer Specific)" % size)
                        continue
                    elif evtype == 0x58: # Time Signature FF 58 04 nn dd cc bb 
                        if read_uint8(tdata) == 0x04: # Make sure
                            nn = read_uint8(tdata)
                            dd = read_uint8(tdata)
                            cc = read_uint8(tdata)
                            bb = read_uint8(tdata)
                            print("Time Signature: %d/%d" % (nn, 2**dd))
                            continue
                    elif evtype == 0x59: # Key Signature FF 59 02 sf mi Key Signature
                        if read_uint8(tdata) == 0x02: # Make sure
                            sf = read_int8(tdata)
                            mi = read_uint8(tdata)
                            print("Key Signature: %s %s (%s%d)" % (
                                "CFBEADG"[(sf + 7 + 4*mi) % 7],
                                "minor" if mi else "Major",
                                "#" if sf >= 0 else "b", abs(sf),
                            ))
                            continue
                    elif evtype == 0x51: # FF 51 03 tttttt Set Tempo
                        if read_uint8(tdata) == 0x03: # Make sure
                            tt2 = read_uint8(tdata)
                            tt1 = read_uint8(tdata)
                            tt0 = read_uint8(tdata)
                            tt = (tt2 << 16) + (tt1 << 8) + (tt0 << 0)
                            print("Set Tempo: %0.3f bpm" % (60e6 / tt))
                            continue
                    elif evtype == 0x06: # FF 06 len <text> Marker
                        size = readVarLen(tdata)
                        text = read_string(tdata, size)
                        print("Marker: %s" % text)
                        continue
                    elif evtype == 0x04: # FF 04 len <text> Instrument name
                        size = readVarLen(tdata)
                        text = read_string(tdata, size)
                        print("Instrument name: %s" % text)
                        continue
                    elif evtype == 0x21: # FF 21 01 pp MIDI Port
                        if read_uint8(tdata) == 0x01: # Make sure
                            port = read_uint8(tdata)
                            print("Port: %d" % port)
                        continue
                    elif evtype == 0x03: # FF 03 length text Track Name
                        size = readVarLen(tdata)
                        text = read_string(tdata, size)
                        print("Track Name: %s" % text)
                        continue
                    elif evtype == 0x2F: # FF 2F 00 End of Track
                        print("----- Track end -----")
                        read_uint8(tdata)
                        reading_track = False
                        continue
                    else:
                        print("Unrecognized event")
                        exit()
                elif (msgtype >> 4) == 0xC: # Program Change
                    ch = msgtype & 0x0F # channel
                    val = read_uint8(tdata)
                    print("Program (instrument) change | Ch=%d Instrument=%d" % (ch, val))
                elif (msgtype >> 4) == 0xB: # Ctrl Change
                    ch = msgtype & 0x0F # channel
                    ctrl = read_uint8(tdata)
                    val = read_uint8(tdata)
                    print("Controller change | Ch=%d Ctrl=%d Val=%d" % (ch, ctrl, val))
                elif (msgtype >> 4) == 0x9: # Note On
                    ch = msgtype & 0x0F # channel
                    key = read_uint8(tdata) & 0x7F
                    vel = read_uint8(tdata) & 0x7F
                    print("Note On | Ch=%d Key=%d (%s) Vel=%d" % (ch, key, note_name(key), vel))
                elif (msgtype >> 4) == 0x8: # Note Off (WOW!)
                    ch = msgtype & 0x0F # channel
                    key = read_uint8(tdata) & 0x7F
                    vel = read_uint8(tdata) & 0x7F
                    print("Note Off | Ch=%d Key=%d (%s) Vel=%d" % (ch, key, note_name(key), vel))
                else:
                    exit()
