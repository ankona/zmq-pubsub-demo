import zmq
import zmq.auth
import time
import lib
import os
import pathlib


exp_path = pathlib.Path(os.getcwd())
client_path = exp_path / "client" / ".smartsim"
server_path = exp_path / "server" / ".smartsim" / "server.key"

server_keys = zmq.auth.load_certificate(server_path)
server_pub = server_keys[0]


context = zmq.Context()

mgr = lib.ListenerManager()


def on_start(msg: lib.StartRequest):
    print(f"I'm handling your newly started item! {msg}")


def on_stop(msg: lib.StopRequest):
    print(f"I'm stopping your trash! {msg}")


mgr.add_listener(
    lib.Listener[lib.StartRequest](
        context, lib.START_PREFIX, client_path, server_pub, on_start
    )
)
# mgr.add_listener(
#     lib.Listener[lib.StopRequest](
#         context, lib.STOP_PREFIX, client_path, server_pub, on_stop
#     )
# )

mgr.connect_all()

while True:
    time.sleep(1)
    mgr.listen()
