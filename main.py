import argparse
import serial

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
    :return: 
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



supported_query_pids = [
    "00",
    "20",
    "40",
    "60",
    "80",
    "A0",
    "C0"
]

supported_pid_list = []

for support_query_index in supported_query_pids:

    try:
        vehicle_response = get_pid("01" + support_query_index + "1")

        formatted_response = format_pid_response_line(vehicle_response[0])

        print(formatted_response)

        range_start = int(formatted_response[0], base=16)

        support_binary_encoded_string = "".join(formatted_response[1])

        support_map = bin(int(support_binary_encoded_string, base=16)).lstrip('0b')

        current_support_map_index = 0
        for pid_index in range(range_start, range_start + 32):
            if support_map[current_support_map_index] == "1":
                supported_pid_list.append("{0:02x}".format(pid_index))
                print("Supports PID {0:02x}".format(pid_index))
            current_support_map_index += 1

    except Exception as e:
        print(e)


for n in range(20):
    for supported_pid in supported_pid_list:
        try:
            print(format_pid_response_line(get_pid("01" + supported_pid)[0]))
        except Exception as e:
            supported_pid_list.remove(supported_pid)
            print(e)




# Home-brew debugging!

# import code
# code.interact(local=dict(globals(), **locals()))
