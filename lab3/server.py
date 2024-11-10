import asyncio


class Server:
    def __init__(self):
        self.clients = set()
        self.rooms = {}
        self.passw = {}

    async def handle(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"Client connected {addr}")
        room_name = ""

        try:
            while True:
                data = await reader.read(100)
                if not data:
                    continue

                message = data.decode()

                if "/get_rooms" in message.split():
                    print(f"get rooms: {message}")
                    writer.write(
                        f"List of rooms: {', '.join(self.rooms.keys())}\n".encode()
                    )
                    await writer.drain()
                    continue

                if "/change_room" in message.split():
                    auth_data = message.split()
                    if len(auth_data) <= auth_data.index("/change_room") + 1:
                        continue

                    new_room_name = auth_data[auth_data.index("/change_room") + 1]
                    new_pwd = ""

                    if len(auth_data) > auth_data.index("/change_room") + 2:
                        new_pwd = auth_data[auth_data.index("/change_room") + 2]

                    addr = writer.get_extra_info("peername")

                    if new_room_name not in self.rooms:
                        self.rooms[new_room_name] = set()
                        self.passw[new_room_name] = new_pwd

                    if new_pwd == self.passw.get(new_room_name, ""):
                        print(
                            f"CLient {addr}, change room {room_name} -> {new_room_name}"
                        )

                        self.rooms[new_room_name].add(writer)

                        if writer in self.rooms.get(room_name, set()):
                            self.rooms[room_name].remove(writer)

                        await self.broadcast("user leaved room\n", writer, room_name)

                        room_name = new_room_name
                    else:
                        writer.write("Invalid password\n".encode())
                        await writer.drain()

                    continue

                await self.broadcast(message, writer, room_name)

        except Exception as e:
            print(e)
        finally:
            print(f"Client {addr} disconnected")
            self.rooms[room_name].remove(writer)
            await self.broadcast(
                f"CLinet {addr} leaved room {room_name}\n", writer, room_name
            )
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, message, sender, room_name):
        # print(message, room_name)
        room = self.rooms.get(room_name, set())
        for client in room:
            try:
                print(room, message)
                client.write(message.encode())
                print(client._buffer)
                await client.drain()
            except:
                continue

    async def run(self, host, port):
        server = await asyncio.start_server(self.handle, host, port)

        addr = server.sockets[0].getsockname()
        print(f"Server started: {addr}")

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    chat_server = Server()
    asyncio.run(chat_server.run("127.0.0.1", 8910))
