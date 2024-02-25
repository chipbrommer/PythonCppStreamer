import socket
import threading


class UDPClient(threading.Thread):
    DEFAULT_TIMEOUT_SECS = 3
    SYNC_1 = 0xA5
    SYNC_2 = 0xE1
    EOB = 0xCB
    COMMAND_MSG_ID = 0x01
    ENABLE_STREAM = 0x01
    DISABLE_STREAM = 0x02
    ENABLE_DISPLAY = 0x03
    DISABLE_DISPLAY = 0x04

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        print(f"[UDP Client] Started on {self.host}:{self.port}")
        self.running = False
        self.stream_enabled = False
        self.display_enabled = False

    def run(self):
        try:
            self.running = True
            while self.running:
                # Set a timeout on the socket
                self.sock.settimeout(self.DEFAULT_TIMEOUT_SECS)

                # Attempt to receive data
                try:
                    data, addr = self.sock.recvfrom(1024)
                except socket.timeout:
                    continue

                # Process the received data
                if data:
                    if len(data) == 5:
                        sync1, sync2, msg_id, command_id, end_byte = data

                        # Check synchronization bytes and end byte
                        if sync1 != self.SYNC_1 or sync2 != self.SYNC_2 or end_byte != self.EOB:
                            continue

                        if msg_id == self.COMMAND_MSG_ID:
                            if command_id == self.ENABLE_STREAM:
                                self.stream_enabled = True
                            elif command_id == self.DISABLE_STREAM:
                                self.stream_enabled = False
                            elif command_id == self.ENABLE_DISPLAY:
                                self.display_enabled = True
                            elif command_id == self.DISABLE_DISPLAY:
                                self.display_enabled = False
                            else:
                                print(f"[UDP Client] Received unrecognized command: {command_id}")
                    else:
                        print("[UDP Client] Received message with invalid length")
        except Exception as e:
            print(f"[UDP Client] An error occurred: {e}")
        finally:
            self.sock.close()

    def stop(self):
        print("[UDP Client] Stopping")
        self.running = False

    def is_stream_enabled(self) -> bool:
        return self.stream_enabled

    def is_display_enabled(self) -> bool:
        return self.display_enabled
