import asyncio


class Server:
    def __init__(self):
        self.clients = {}
        self.rooms = {}
        self.passw = {}
        self.user_data = {}
    
    def find_writer_by_username(self, username):
        for writer, user_data in self.user_data.items():
            if user_data['username'] == username:
                return writer
        return None
    
    async def handle(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"Client connected {addr}")
        room_name = ""
        username = None #Store username per client.

        try:
            # Receive username from the client (assuming it's sent immediately after connecting)
            username_data = await reader.readuntil(b'\n')  
            username = username_data.strip().decode()

            if not username:
                writer.write(b"Username not received. Disconnecting.\n")
                await writer.drain()
                return #Disconnect if no username is received

            self.user_data[writer] = {'username': username}
            print(f"Client {username} ({addr}) connected.")

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

                if "/pm" in message.split():
                    auth_data = message.split()
                    if len(auth_data) < 3:
                        writer.write(b"Usage: /pm <username> <message>\n")
                        await writer.drain()
                        continue

                    target_username = auth_data[1]
                    message_to_send = " ".join(auth_data[2:]) #Get the message part.

                    target_writer = self.find_writer_by_username(target_username)
                    if target_writer is None:
                        writer.write(f"User '{target_username}' not found.\n".encode())
                        await writer.drain()
                        continue

                    #Send PM. No need for a separate room in this implementation.
                    target_writer.write(f"PM from {username}: {message_to_send}\n".encode())
                    await target_writer.drain()
                    continue

                await self.broadcast(message, writer, room_name)

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            print(f"Client {addr} disconnected")
            if writer in self.user_data:
                del self.user_data[writer] #Remove user data on disconnect.
            if room_name: #Check if there was a room to remove the client from.
                self.rooms.get(room_name, set()).discard(writer)  #Use discard to safely remove
            await self.broadcast(
                f"Client {username or addr} leaved room {room_name}\n", writer, room_name
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
