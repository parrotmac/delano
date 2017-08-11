import argparse
import serial
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port')
parser.add_argument('-b', '--baud', default=115200)
args = parser.parse_args()

if not args.port:
    print("Please specify a serial port with --port")
    print("For a list of available ports run `python -m serial.tools.list_ports`")
    exit(-1)


conn = serial.Serial(args.port, args.baud)

if conn.in_waiting:
    print(conn.read_all())


# <---------->
# BEGIN: ATD

def initialize_cmd_ATD():
    conn.write("ATD\r")
    conn.flush()

    buffer = ""
    character_found = False
    while (not character_found):
        buffer += conn.read_all()
        if ">" in buffer:
            character_found = True

    cleaned_buffer = buffer.split('\r')

    if "ATD" not in cleaned_buffer or "OK" not in cleaned_buffer or ">" not in cleaned_buffer:
        raise Exception("Device not reset")


initialize_cmd_ATD()

print("Device settings reset")

# END: ATD
# <////////////>





# <---------->
# BEGIN: ATS1

conn.write("ATS1\r")
conn.flush()

buffer = ""
character_found = False
while(not character_found):
    buffer += conn.read_all()
    if ">" in buffer:
        character_found = True

cleaned_buffer = buffer.split('\r')

if "OK" not in cleaned_buffer or ">" not in cleaned_buffer:
    print("Spaces may not be on")
    exit(-1)
print("Spaces are on")

# END: ATA1
# <////////////>





# <---------->
# BEGIN: ATE0

conn.write("ATE0\r")
conn.flush()

buffer = ""
character_found = False
while(not character_found):
    buffer += conn.read_all()
    if ">" in buffer:
        character_found = True

cleaned_buffer = buffer.split('\r')

if "OK" not in cleaned_buffer or ">" not in cleaned_buffer:
    print("Line endings didn't turn off")
    exit(-1)
print("Line endings are off")

# END: ATE0
# <////////////>




# <---------->
# BEGIN: AUTOMATIC PROTOCOL SELECTION

conn.write("ATSP00\r")
conn.flush()

buffer = ""
character_found = False
while(not character_found):
    buffer += conn.read_all()
    if ">" in buffer:
        character_found = True

cleaned_buffer = buffer.split('\r')

if "ERROR" in buffer:
    print("Bus initialization error")
    exit(-1)

print("Bus initialization complete")

# END: AUTOMATIC PROTOCOL SELECTION
# <////////////>



# <---------->
# BEGIN: BUS INIT

conn.write("0100\r")
conn.flush()

buffer = ""
character_found = False
while(not character_found):
    buffer += conn.read_all()
    if ">" in buffer:
        character_found = True

cleaned_buffer = buffer.split('\r')

if "ERROR" in buffer:
    print("Bus initialization error")
    exit(-1)

print("Bus initialization complete")

# END: BUS INIT
# <////////////>


def get_pid(pid):
    """
    Blah
    :param pid: Code such as 010C 
    :return: A list of lines from ELM response
    """
    conn.write("{}\r".format(pid))
    conn.flush()

    stop_hit = False
    temp_buffer = ""
    while(not stop_hit):
        temp_buffer += conn.read(conn.in_waiting)

        stop_hit = ">" in temp_buffer

    new_buffer = []
    for buffer_item in temp_buffer.split('\r'):

        if buffer_item is '' or buffer_item is '>':
            continue

        new_buffer.append(buffer_item.strip())

    if "NO DATA" in new_buffer:
        raise Exception("No data available from device")

    return new_buffer

def format_pid_response_line(pid_response_line):
    split_response = pid_response_line.split(" ")

    query_name = split_response[1]
    query_data = split_response[2:]

    return (query_name, query_data)


def get_vin():

    raw_vin_response = get_pid("09025") # Assume 5 lines of response

    encoded_vin = ""
    for res_line in raw_vin_response:
        encoded_vin += "".join(res_line.split(" ")[3:])

    decoded_vin = encoded_vin.decode('hex').lstrip('\x00')

    return decoded_vin


def get_rpm():
    scan_result = get_pid("010C")[0].split(" ")

    ayy = int(scan_result[2], 16)
    bee = int(scan_result[3], 16)

    return ((256 * ayy) + bee ) / 4


def get_mph():
    return float(int(get_pid("010D")[0].split(" ")[2], 16)) * 0.621371





def get_year_from_vin(vin_number):

    numeric_position_7_codes = {
        "A": 1980,
        "B": 1981,
        "C": 1982,
        "D": 1983,
        "E": 1984,
        "F": 1985,
        "G": 1986,
        "H": 1987,
        "J": 1988,
        "K": 1989,
        "L": 1990,
        "M": 1991,
        "N": 1992,
        "P": 1993,
        "R": 1994,
        "S": 1995,
        "T": 1996,
        "V": 1997,
        "W": 1998,
        "X": 1999,
        "Y": 2000,
        "1": 2001,
        "2": 2002,
        "3": 2003,
        "4": 2004,
        "5": 2005,
        "6": 2006,
        "7": 2007,
        "8": 2008,
        "9": 2009
    }

    alpha_position_7_codes = {
        "A": 2010,
        "B": 2011,
        "C": 2012,
        "D": 2013,
        "E": 2014,
        "F": 2015,
        "G": 2016,
        "H": 2017,
        "J": 2018,
        "K": 2019,
        "L": 2020,
        "M": 2021,
        "N": 2022,
        "P": 2023,
        "R": 2024,
        "S": 2025,
        "T": 2026,
        "V": 2027,
        "W": 2028,
        "X": 2029,
        "Y": 2030,
        "1": 2031,
        "2": 2032,
        "3": 2033,
        "4": 2034,
        "5": 2035,
        "6": 2036,
        "7": 2037,
        "8": 2038,
        "9": 2039
    }

    vin_year_code = vin_number[9]

    if vin_number[6].isdigit():
        return numeric_position_7_codes[vin_year_code]

    return alpha_position_7_codes[vin_year_code]


# supported_query_pids = [
#     "00",
#     "20",
#     "40",
#     "60",
#     "80",
#     "A0",
#     "C0"
# ]
#
# supported_pid_list = []
#
# no_data_errors = defaultdict(int)
#
# for support_query_index in supported_query_pids:
#
#     try:
#         vehicle_response = get_pid("01" + support_query_index + "1")
#
#         formatted_response = format_pid_response_line(vehicle_response[0])
#
#         print(formatted_response)
#
#         range_start = int(formatted_response[0], base=16)
#
#
#         encoded_support_map_encoded = "".join(formatted_response[1])
#
#         support_map = bin(int(encoded_support_map_encoded, base=16)).lstrip('0b')
#         print("support_map: {}".format(support_map))
#
#         current_support_map_index = 0
#         print("Range: {}:{}".format(range_start, range_start+32))
#         for pid_index in range(range_start, range_start + 32):
#             print("support_map[{}]: {}".format(current_support_map_index, support_map[current_support_map_index]))
#             if support_map[current_support_map_index] == "1":
#                 supported_pid_list.append("{0:02x}".format(pid_index))
#                 print("Supports PID {0:02x}".format(pid_index))
#             current_support_map_index += 1
#
#     except Exception as e:
#         print("{}: ".format(support_query_index, e))
#
#
# for n in range(2):
#     for supported_pid in supported_pid_list:
#         try:
#             print(format_pid_response_line(get_pid("01" + supported_pid)[0]) + "1") # Assume 1-line responses
#         except Exception as e:
#             pass
#             # supported_pid_list.remove(supported_pid)
#             # print(e)


# _fake_pid_list = []
#
# for i in range(180):
#     _fake_pid_list.append("{0:02x}".format(i))
#
# for unknown_pid in _fake_pid_list:
#     try:
#         print(format_pid_response_line(get_pid("01" + unknown_pid)[0]))
#     except Exception as e:
#         no_data_errors[unknown_pid] += 1
#         # supported_pid_list.remove(supported_pid)
#         # print(e)




# Home-brew debugging!

import code
code.interact(local=dict(globals(), **locals()))
