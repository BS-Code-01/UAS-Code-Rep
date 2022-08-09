import codecs
import os
import binascii

# path = "D:/temp00_Masterarbeit/temp5/"
# log_file_name = "00000052.BIN"
# log_file = os.path.join(path, log_file_name)

path_logfile      = "D:/temp00_Masterarbeit/temp5/"
logfile_name      = "00000052.BIN"
# logfile_name      = "14_55_37.ulg"
logfile_full_path = os.path.join(path_logfile, logfile_name)

with open(logfile_full_path, "rb") as log_file_read:
    # readbytes = log_file_read.read(100)
    readbytes = log_file_read.read(1000)
    # print(type(readbytes))
    # print(len(readbytes))
    print(readbytes)

    # hexstring = str(readbytes)[2:].replace("\\x", "")
    # hexstring = str(readbytes)
    # print(hexstring)
    # print(len(hexstring))
    # print(type(hexstring))
    # s = hexstring.decode("hex")
    # print(s)

    # byte_array = bytearray.fromhex(hexstring)
    # s = byte_array.decode()
    # print(s)

    # binary_string = binascii.unhexlify(hexstring)
    # print(binary_string)
    # print(type(binary_string))

    # def byte_to_binary(n):
    #     return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))
    #
    # def hex_to_binary(h):
    #     return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))
    #
    # print(hex_to_binary(hexstring))

    # s = readbytes.bit_length() + 7
    # # s = (readbytes.bit_length() + 7) // 8, 'big').decode()
    # print(s)

    # print(readbytes.find(b"\n"))

    # s = readbytes.decode('UTF-8')
    # s = codecs.decode(readbytes, 'UTF-8')
    # s = codecs.decode(readbytes)
    # s = str(readbytes, 'UTF-8')
    # print(s)

    # bytearray_ = bytearray(readbytes)
    # print(bytearray_)
    # for byte in bytearray_:
    #     print(byte)
    #     print(type(byte))

    # for byte in log_file_read.read(50):
    #     print(type(byte))
    #     print(hex(byte))
    #     print(bin(byte))
    #     print(int(byte))
