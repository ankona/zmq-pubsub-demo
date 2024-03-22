import zmq
import zmq.auth
import zmq.auth.thread
import lib
import time
import os
import pathlib
import typing as t


exp_path = pathlib.Path(os.getcwd())


def auth_folder(exp_path: str) -> pathlib.Path:
    return pathlib.Path(exp_path) / ".smartsim"


def init_auth(exp_path: str, cert_name: str):
    exp_name = "exp123"
    # cert_name = f"{exp_name}_cert"

    auth_path = auth_folder(exp_path)
    auth_path.mkdir(parents=True, exist_ok=True)

    cert_files = zmq.auth.create_certificates(
        auth_path, cert_name, {"exp": exp_name, "exp_path": exp_path}
    )
    return cert_files


def load_auth(auth_path: str) -> t.Dict[bytes, bool]:
    # auth_path = auth_folder(exp_path)
    public = zmq.auth.load_certificate(auth_path[0])
    private = zmq.auth.load_certificate(auth_path[1])
    return public, private


server_path = exp_path / "server"
client_path = exp_path / "client"

server_cert_paths = init_auth(server_path, "server")
print(server_cert_paths)

client_cert_paths = init_auth(client_path, "client")
print(client_cert_paths)

server_keys = load_auth(server_cert_paths)
client_keys = load_auth(client_cert_paths)

context = zmq.Context()

# Start an authenticator for this context.
auth = zmq.auth.thread.ThreadAuthenticator(context)
auth.start()
auth.allow("127.0.0.1")
# Tell authenticator to use the certificate in a directory
auth.configure_curve(domain="*", location=server_path)

server = context.socket(zmq.PUSH)
server.curve_publickey = server_keys[1][0]
server.curve_secretkey = server_keys[1][1]
server.curve_server = True

server.bind("tcp://*:5555")

n = 50000


while True:
    time.sleep(5)

    start = lib.StartRequest(num=n)
    stop = lib.StopRequest(num=n + 7456)
    n += 1

    print(f"sending start req: {start.num}")
    key = start.key()
    # server.send_string(f"{key}{start.model_dump_json()}")
    server.send(b"hey")

    # key = stop.key()
    # print(f"sending stop req: {stop.num}")
    # server.send_string(f"{key}{stop.model_dump_json()}")



