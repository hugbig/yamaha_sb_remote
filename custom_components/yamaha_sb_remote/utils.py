import logging

_LOGGER = logging.getLogger(__name__)


def create_command_code(command):
    if len(command) == 1: #single action type
        command = command[0]
        if command == 'handshake': data = bytearray([0x01,0x48,0x54,0x54,0x20,0x43,0x6f,0x6e,0x74])
        elif command == 'powerOn': data = bytearray([0x40,0x78,0x7e])
        elif command == 'powerOff': data = bytearray([0x40,0x78,0x7f])
        elif command == 'TV': data = bytearray([0x40,0x78,0xdf])
        elif command == 'Optical': data = bytearray([0x40,0x78,0x49])
        elif command == 'Analog': data = bytearray([0x40,0x78,0xd1])
        elif command == 'subUp': data = bytearray([0x40,0x78,0x4c])
        elif command == 'subDown': data = bytearray([0x40,0x78,0x4d])
        elif command == 'muteOn': data = bytearray([0x40,0x7e,0xa2])
        elif command == 'muteOff': data = bytearray([0x40,0x7e,0xa3])
        elif command == 'Movie': data = bytearray([0x40,0x78,0xd9])
        elif command == 'Game': data = bytearray([0x40,0x78,0xdc])
        elif command == 'clearVoiceOn': data = bytearray([0x40,0x7e,0x80])
        elif command == 'clearVoiceOff': data = bytearray([0x40,0x7e,0x82])
        elif command == 'bassOn': data = bytearray([0x40,0x78,0x6e])
        elif command == 'bassOff': data = bytearray([0x40,0x78,0x6f])
        elif command == 'ledBright': data = bytearray([0x51,0x00])
        elif command == 'ledDim': data = bytearray([0x51,0x01])
        elif command == 'ledOff': data = bytearray([0x51,0x02])
        elif command == 'request': data = bytearray([0x03, 0x05])
        elif command == 'blue': data = bytearray([0x40, 0x78,0x34])
        elif command == 'dim': data = bytearray([0x40, 0x78,0xba])
        else:
            _LOGGER.warning("Invalid command sending req instead")
            data = bytearray([0x03, 0x05]) #Sends req instead
    elif len(command) == 2: #volume is the only time this is used that we know of
        if command[0] == 'volumeSet': data = bytearray([0x41, command[1]])
        else:
            _LOGGER.warning("Invalid command")
            data = bytearray([0x03, 0x05]) #Sends a req instead    
    else:
        _LOGGER.warning("Bad command format, too long") #command was too long
        data = bytearray([0x03, 0x05]) #Sends a req instead    
    data.insert(0, len(data))
    data.append(checksum_make(data))
    data.insert(0, 0xaa)
    data.insert(0, 0xcc)
    return bytes(data)        

def checksum_byte(input):
    #checks the checksum of the data as a byte array (two's complement of the sum from the length byte)
    return checksum_make(input[2:-1]) == input[-1]

def checksum_make(input):
    #creates a checksum from byte array and returns int: the two's complement of the sum, on 8 bits
    return (-sum(input)) & 0xFF

def interpret_message(val):
    #interprets a byte array message
    length = val[2]
    if length == 0x02:
        if val[3] == 0x10: #power
            if val[4] == 0x10: return "Power OFF"
            elif val[4] == 0x11: return "Power ON"
        elif val[3] == 0x11: #input
            if val[4] == 0x05: return "Bluetooth"
            if val[4] == 0x07: return "TV"
            if val[4] == 0x0A: return "Optical"
            if val[4] == 0x0C: return "Analog"
        elif val[3] == 0x13: #sub
            return "Subwoofer to: " + str(val[4])
        elif val[3] == 0x24: #led
            if val[4] == 0x02: return "LED Off"
            elif val[4] == 0x01: return "LED Dim"
            elif val[4] == 0x00: return "LED Bright"
    elif length == 0x03:
        if val[3] == 0x12:
            if val[4] == 0x01:
                return "Volume Message, Mute ON, volume: " + str(val[5])
            elif val[4] == 0x00:
                return "Volume Message, Mute OFF, volume: " + str(val[5])
    elif length == 0x05:
        if val[3] == 0x15: #style
            if val[4] != 0x00: "Unknown message: 0x" + (val.hex())

            if val[5] == 0x00:
                surround_string = "Off"
            elif val[5] == 0x01:
                surround_string = "On"
            else: "Unknown message: 0x" + (val.hex())

            if val[6] == 0x03: #movie
                style_string = "Movie"
            elif val[6] == 0x0c: #game
                style_string = "Game"
            elif val[6] == 0x0a: #standard
                style_string = "Standard"
            else: "Unknown message: 0x" + (val.hex())

            if val[7] == 0x00:
                voice_string = "Off"
                bass_string = "Off"
            elif val[7] == 0x20:
                voice_string = "Off"
                bass_string = "On"
            elif val[7] == 0x04:
                voice_string = "On"
                bass_string = "Off"
            elif val[7] == 0x24:
                voice_string = "On"
                bass_string = "On"
            else: "Unknown message: 0x" + (val.hex())
            return "Style Message, [Surround " + surround_string + "][Style " + style_string + "][Clear Voice " + voice_string + "][Bass Extension " + bass_string + "]"
    return "Unknown message: 0x" + (val.hex())
