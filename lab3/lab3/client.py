import asyncio
import tkinter as tk
from tkinter import scrolledtext, simpledialog

class Client:
    def __init__(self, root, loop):
        self.root = root
        self.loop = loop
        self.name = simpledialog.askstring("Name", "Enter name:")
        self.room = ""
        self.writer: asyncio.StreamWriter = None
        self.reader: asyncio.StreamReader = None
        self.initialize_gui()

    def initialize_gui(self):
        self.root.title(f"Чат - {self.name}")
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH)

        self.entry = tk.Entry(self.root)
        self.entry.pack(expand=True, fill=tk.X)
        self.entry.bind("<Return>", self.send)

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection("127.0.0.1", 8910)
        #Get username from server
        self.writer.write(self.name.encode() + b'\n')
        await self.writer.drain()


        self.loop.create_task(self.start_receive())

    async def start_receive(self):
        while True:
            data = await self.reader.read(100)
            message = data.decode()
            print(message, self.name)
            self.text_area.insert(tk.END, message)

    def send(self, event):
        message = self.entry.get()
        words = message.split()

        if "/change_room" in words:
            new_room = words[words.index("/change_room") + 1]
            self.room = new_room
            print(f"new room {self.room}")

        if "/pm" in words:
            target = words[1]
            msg = " ".join(words[2:])
            self.writer.write(f"/pm {target} {msg}\n".encode()) #Send /pm command to server

        elif message: # Send normal message only if it's not a command.
            self.writer.write(f"{self.name}: {message}\n".encode())
    
        self.entry.delete(0, tk.END)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    root = tk.Tk()
    T = tk.Text(root, height=5, width=52)
    T.pack()
    T.insert(tk.END, "* `/get_rooms` - print list of rooms\n* `/change_room [room] [password]` - join to [room]\n* `/pm [username] [message]` - send private message")
    client = Client(root, loop)

    async def tkUpdate():
        while True:
            root.update()
            await asyncio.sleep(0.05)

    try:
        loop.run_until_complete(
            asyncio.gather(
                loop.create_task(tkUpdate()),
                loop.create_task(client.connect()),
            )
        )
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        loop.close()