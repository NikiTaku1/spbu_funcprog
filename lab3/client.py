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

        if "/change_name" in words:
            self.name = words[words.index("/change_name") + 1]

        if "/change_room" in words:
            self.room = words[words.index("/change_room") + 1]
            print(f"new room {self.room}")

        if message:
            self.writer.write(f"{self.name}: {message}\n".encode())
            self.entry.delete(0, tk.END)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    root = tk.Tk()
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
