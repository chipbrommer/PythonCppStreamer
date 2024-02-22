import socket
import threading


class TCPServer(threading.Thread):
    DEFAULT_TIMEOUT_SECS = 3

    def __init__(self, host, port, message_handler):
        super().__init__()
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.running = True

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[TCP Server] Started on {self.host}:{self.port}")
        self.accept_clients()

    def accept_clients(self):
        self.server_socket.settimeout(self.DEFAULT_TIMEOUT_SECS)
        
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                if self.running:  # Check if the server is still running
                    print(f"[TCP Server] Connection established with {client_address}")
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.start()
                    self.clients.append((client_socket, client_thread))
                else:
                    # If the server is not running, close the client socket
                    client_socket.close()
            except socket.timeout:
                pass
            except Exception as e:
                print(f"[TCP Server] Error accepting client connection: {e}")
                
        # Close the server socket after all client connections have been processed
        self.server_socket.close()

    def handle_client(self, client_socket):
        client_socket.settimeout(self.DEFAULT_TIMEOUT_SECS)
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    # If no data is received, client has disconnected
                    print(f"[TCP Server] Client {client_socket.getpeername()} disconnected")
                    break  # Exit the loop to stop handling this client
                # Pass the received data to the message handler
                self.message_handler(data)
            except socket.timeout:
                # Handle timeout (no data received within the timeout period)
                pass
            except Exception as e:
                print(f"[TCP Server] Error handling client: {e}")
                break  # Exit the loop if an error occurs

        # Close the client socket and remove it from the list of active connections
        client_socket.close()
        self.clients.remove((client_socket, threading.current_thread()))

    def stop(self):
        print("[TCP Server] Stopping")
        self.running = False
        for client_socket, client_thread in self.clients:
            client_socket.close()
            client_thread.join()

    def get_num_connections(self):
        return len(self.clients)

    def send_message(self, message):
        for client_socket, _ in self.clients:
            client_socket.sendall(message)

    def receive_message(self):
        messages = []
        for client_socket, _ in self.clients:
            try:
                data = client_socket.recv(1024)
                if data:
                    messages.append(data.decode())
            except Exception as e:
                print(f"[TCP Server] Error receiving message: {e}")
        return messages
