import zmq
import time
import lib


context = zmq.Context()

mgr = lib.ListenerManager()


def on_start(msg: lib.StartRequest):
    print(f"I'm handling your newly started item! {msg}")


def on_stop(msg: lib.StopRequest):
    print(f"I'm stopping your trash! {msg}")


mgr.add_listener(lib.Listener[lib.StartRequest](context, lib.START_PREFIX, on_start))
mgr.add_listener(lib.Listener[lib.StopRequest](context, lib.STOP_PREFIX, on_stop))

mgr.connect_all()

while True:
    time.sleep(1)
    mgr.listen()
