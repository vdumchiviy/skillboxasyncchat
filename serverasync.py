import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport
    tmp_login: str = None
    tmp_list: list

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data)
        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.tmp_login = decoded.replace(
                    "login:", "").replace("\r\n", "")
                if self.server.clients_login.count(self.tmp_login) > 0:
                    self.transport.write(
                        f"Error! The login {self.tmp_login} is busy!\n".encode(
                        )
                    )
                    self.server.close
                else:
                    self.login = self.tmp_login
                    self.server.clients_login.append(self.login)
                    self.transport.write(
                        f"Hello, {self.login}!\r\n".encode()
                    )
                    self.send_history()
            else:
                self.transport.write("Incorrect login!\n".encode())
            self.tmp_login = None

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("пришел новый клиент!")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        if self.login is not None:
            self.server.clients_login.remove(self.login)
        print("Клиент вышел!")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"
        for user in self.server.clients:
            user.transport.write(message.encode())

        # print("======================================================")
        # print("Список изначальный:\n", "+".join(self.server.messages_10))

        self.server.messages_10.append(message)
        # print("Список добавленный:\n", "+".join(self.server.messages_10))

        self.server.messages_10.reverse()
        # print("Список перевернутый:\n", "+".join(self.server.messages_10))

        self.server.messages_10 = self.server.messages_10[0:10]
        # print("Список 10:\n", "+".join(self.server.messages_10))

        self.server.messages_10.reverse()
        print("Список итоговый:\n", "+".join(self.server.messages_10))

    def send_history(self):
        print("    ---- ServerProtocol.send_history")
        self.transport.write(''.join(self.server.messages_10).encode())


class Server:
    clients: list
    clients_login: list
    messages_10: list

    def __init__(self):
        self.clients = []
        self.clients_login = list()
        self.messages_10 = list()
        print("    ---- Server.__init__")

    def build_protocol(self):

        print("    ---- Server.build_protocol")
        return ServerProtocol(self)

    async def start(self):
        print("    ---- Server.start")
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )
        print("Сервер запущен")
        await coroutine.serve_forever()


process = Server()
try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручнуб")
