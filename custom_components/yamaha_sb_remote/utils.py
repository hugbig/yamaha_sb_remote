import logging

_LOGGER = logging.getLogger(__name__)

LED_val = ["Bright", "Dim", "Off"]
Subwoofer = {0:-4,4:-3,8:-2,12:-1,16:0,20:1,24:2,28:3,32:4}
Style_val = {3:"Movie",10:"Standard",12:"Game"}
Input_val={5:"Bluetooth",7:"TV",10:"Optical",12:"Analog"}

def create_command_code(command, device=False):
    if len(command) == 1: #single action type
        command = command[0]
        if command == 'handshake': data = bytearray([0x01,0x48,0x54,0x54,0x20,0x43,0x6f,0x6e,0x74])
        elif command == 'powerOn': data = bytearray([0x40,0x78,0x7e])
        elif command == 'powerOff': data = bytearray([0x40,0x78,0x7f])
        elif command == 'powerToggle':
            if device._power == True: return create_command_code(['powerOff'])
            else: return create_command_code(['powerOn'])
        elif command == 'Bluetooth': data = bytearray([0x40,0x78,0x29])
        elif command == 'TV': data = bytearray([0x40,0x78,0xdf])
        elif command == 'Optical': data = bytearray([0x40,0x78,0x49])
        elif command == 'Analog': data = bytearray([0x40,0x78,0xd1])
        elif command == 'subUp': data = bytearray([0x40,0x78,0x4c])
        elif command == 'subDown': data = bytearray([0x40,0x78,0x4d])
        elif command == 'muteOn': data = bytearray([0x40,0x7e,0xa2])
        elif command == 'muteOff': data = bytearray([0x40,0x7e,0xa3])
        elif command == 'muteToggle':
            if device._mute == True: return create_command_code(['muteOff'])
            else: return create_command_code(['muteOn'])
        elif command == 'Standard': data = bytearray([0x40,0x7e,0xf1])
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

def checksum_int(input):
    #checks the checksum of the data as an int expects removal of 0xCCAA but keep length byte and checksum
    input = input.to_bytes(len(hex(input)), 'big')
    return checksum_byte(input)


def checksum_byte(input):
    #checks the checksum of the data as a byte array
    sum = 0
    for i in input[2:-1]:
        sum += i
    sum = ~ sum #invert
    sum = sum & 255 #take last 8 bits
    sum += 1
    if (sum != input[-1]):
        return False
    else:
        return True

def checksum_make(input):
    #creates a checksum from byte array and returns int
    sum = 0
    for i in input:
        sum += i
    sum = ~ sum #invert
    sum = sum & 255 #take last 8 bits
    sum += 1
    return sum

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

def set_by_hex(data, device): 
    _LOGGER.debug(hex(data))
    if (data >> 104 != 0xccaa0e0500):
        _LOGGER.warning("Missing expected 0xccaa0e0500 at start of data")
    if (data >> 40) & 16777215 != 0x202000:
        _LOGGER.warning("Missing expected 0x202000 in data")
    cleaned_data = data & (0x10 ** 32 - 1) #strip 0xCCAA given fixed length
    if not checksum_int(cleaned_data):
        _LOGGER.warning("Bad checksum in data")
    device._status = "init"
    if device._type == "media_player" :
        device._power = bool((data >> 96) & 1)
        device._current_source = Input_val[(data >> 88) & 0xff]
        device._muted  = bool((data >> 80) & 1)
        volume = (data >> 72) & 0xff
        device._volume = (volume * 1.666) / 100
        device._sound_mode = Style_val[(data >> 24) & 0xff]
    elif device._type == "clear_voice" :
        device._power = bool((data >> 18) & 1)
    elif device._type == "bass_ext" :
        device._power = bool((data >> 21) & 1)
    elif device._type == "subwoofer" :  
        device._sub = Subwoofer[(data >> 64) & 0xff]
    elif device._type == "led" :  
        device._led = LED_val[(data >> 8) & 0x3]    
    else :
        _LOGGER.warning("Invalid device type")    
    return device