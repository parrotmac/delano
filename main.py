import base64

import serial

serial_address = "/dev/cu.usbserial-STY0CNSO"
baud_rate = 115200

conn = serial.Serial(serial_address, baud_rate)

if conn.in_waiting:
    print(conn.read_all())





# <---------->
# BEGIN: ATD

conn.write("ATD\r")
conn.flush()

buffer = ""
character_found = False
while(not character_found):
    buffer += conn.read_all()
    if ">" in buffer:
        character_found = True

cleaned_buffer = buffer.split('\r')

if "ATD" not in cleaned_buffer or "OK" not in cleaned_buffer or ">" not in cleaned_buffer:
    print("Device not reset")
    exit(-1)
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

supported_pid_maps = []

for support_query_index in supported_query_pids:
    vehicle_response = get_pid("01" + support_query_index)

    formatted_response = format_pid_response_line(vehicle_response[0])







import code
code.interact(local=dict(globals(), **locals()))
