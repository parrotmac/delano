# Delano

Delano is a Python library for communicating with the ELM327-based Serial-to-OBD2 adapters.

---

## Usage
`python main.py --port <path_or_name_of_your_ELM327>`

Delano then attemps to setup communication with the device, and defines a few helper functions. After printing the current status, Delano jumps to a Python interpreter prompt (`>>>`) with all local variables imported.

### `get_pid(pid)`

Params:
 - `pid`: The OBD2 PID
 
Returns:
  ELM327's response pre-separated at spaces, and by lines.
  
Note: The `get_pid(pid)` function accepts more than OBD2 pids. Under the hood it's simply writing out the value of `pid` with a carrage return (`\r`) at the end, then formatting the device's response. Because of this simplicity, it can be combined with the ELM327's CAN engine to inject CAN frames directly onto the bus. Simply pass your frame as the `pid`.
