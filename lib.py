from abc import abstractclassmethod, abstractmethod
from pydantic import BaseModel
import pathlib
import typing as t
import zmq
import zmq.auth

START_PREFIX = "START:"
STOP_PREFIX = "STOP:"


class Request(BaseModel):
    num: int = 0

    @abstractclassmethod
    def key(self) -> str: ...

    @property
    def message_key(self):
        return self.key()


class StartRequest(Request):
    @classmethod
    def key(cls) -> str:
        return START_PREFIX

    @property
    def target(self) -> str:
        return "/foo/bar/exe"


class StopRequest(Request):
    @classmethod
    def key(cls) -> str:
        return STOP_PREFIX

    @property
    def target(self) -> int:
        # pretend it's an integer pid...
        return 99


TMsg = t.TypeVar("TMsg")


class Listener(t.Generic[TMsg]):
    def __init__(
        self,
        context: zmq.Context,
        prefix: str,
        keys_dir: str,
        server_pub_key: bytes,
        handler: t.Callable[[TMsg], None],
    ):
        self.context: zmq.Context = context
        self.socket: zmq.Socket = context.socket(zmq.PULL)
        self._handler = handler
        self._prefix = prefix
        self._keys_dir = keys_dir
        self._server_pub_key = server_pub_key

    def connect(self) -> None:
        client_secret_file = pathlib.Path(self._keys_dir) / "client.key_secret"
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)

        self.socket.curve_secretkey = client_secret
        self.socket.curve_publickey = client_public
        self.socket.curve_serverkey = self._server_pub_key

        self.socket.connect("tcp://127.0.0.1:5555")
        # self.socket.subscribe(self.prefix)

    @property
    def prefix(self) -> str:
        return self._prefix

    def listen(self) -> None:
        msg = self.socket.recv_string()
        msg = msg.split(self.prefix)[-1]

        model = self.__orig_class__.__args__[0].model_validate_json(msg)

        self._handler(model)


class ListenerManager:
    def __init__(self):
        self._listeners: t.List[Listener] = []

    def add_listener(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def connect_all(self) -> None:
        self._poller = zmq.Poller()

        for listener in self._listeners:
            listener.connect()
            self._poller.register(listener.socket, zmq.POLLIN)

    def listen(self) -> None:
        sockets = {l.socket: l for l in self._listeners}
        socks: t.Dict[zmq.Socket, int] = dict(self._poller.poll(3))

        for sock, rc in socks.items():
            listener = sockets.get(sock)
            listener.listen()
