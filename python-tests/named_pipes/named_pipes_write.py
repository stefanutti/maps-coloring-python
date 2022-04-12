#!/usr/local/bin/python3
# writer.py
import os
import struct


def encode_msg_size(size: int) -> bytes:
    return struct.pack("<I", size)


def decode_msg_size(size_bytes: bytes) -> int:
    return struct.unpack("<I", size_bytes)[0]


def create_msg(content: bytes) -> bytes:
    size = len(content)
    return encode_msg_size(size) + content


if __name__ == "__main__":
    IPC_FIFO_NAME = "hello_ipc"

    fifo = os.open(IPC_FIFO_NAME, os.O_WRONLY)
    try:
        while True:
            name = input("Enter a name: ")
            content = f"Hello {name}!".encode("utf8")
            msg = create_msg(content)
            os.write(fifo, msg)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        os.close(fifo)
