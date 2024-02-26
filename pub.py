import zmq
import lib
import time


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555", )

n = 50000

while True:
    time.sleep(1)

    start = lib.StartRequest(num=n)
    stop = lib.StopRequest(num = n + 7456)
    n += 1
    
    print(f"sending start req: {start.num}")
    key = start.key()
    socket.send_string(f"{key}{start.model_dump_json()}")
    
    key = stop.key()
    print(f"sending stop req: {stop.num}")
    socket.send_string(f"{key}{stop.model_dump_json()}")
