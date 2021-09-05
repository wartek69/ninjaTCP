import socket

class TcpServerEcho:
    """Simple echo tcp server, just echos the received bytes.
    """
    def __init__(self):
        self.host = '127.0.0.1'  # Standard loopback interface address (localhost)
        self.port = 65432        # Port to listen on (non-privileged ports are > 1023)
        self.start_server()

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f'Connected by {addr}')
                while True:
                    data = conn.recv(8192)
                    if not data:
                        break
                    conn.sendall(data)

if __name__=='__main__':
    tcp_server = TcpServerEcho()
