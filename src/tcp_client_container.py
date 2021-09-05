#!/usr/bin/python3
import time
import asyncio
import signal
import queue
from tcp_client import TcpClient
from pubsub import pub

class TcpClientContainer():
    """
    TcpClientContainer: Container that manages the tcp client
    """

    def __init__(self):
        self.tcp_ip = '127.0.0.1'
        self.tcp_port = 65432
        self.tcp_client = TcpClient(self.tcp_ip, self.tcp_port)
        pub.subscribe(self.__reconnect_tcpclient, 'reconnect_tcp_client')
        pub.subscribe(self.__handle_tcp_client_errors, 'error_handler')

        self.loop = asyncio.get_event_loop()
        self.loop.call_soon(self.iterate)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def __reconnect_tcpclient(self):
        """Disposes and reinitialises the tcp client
        """
        print('Reconnecting tcp client in 1sec!')
        self.tcp_client.dispose()
        time.sleep(1)
        self.tcp_client = TcpClient(self.tcp_ip, self.tcp_port)
    
    def __handle_tcp_client_errors(self, error):
        """Handles errors thrown by the tcp client
        """
        print(f'Received following error fro the tcp client {repr(error)}')


    def iterate(self):
        try:
            try:
                message_bytes = self.tcp_client.received_messages_buffer.get(block=False)
                message_str = message_bytes.decode('utf-8')
                #print(f'received following message: {message_str}')
            except queue.Empty:
                #Nothing to receive
                pass
            self.tcp_client.send_data(b'Hello World')

        except Exception as e:
            error_msg = 'Received an unexpected exception in tcp connection handler: ' + repr(e)
            print(error_msg)
        
        self.loop.call_later(0.0001, self.iterate)
    

    def exit_gracefully(self, signum, frame):
        self.loop.stop()
        self.close(True)

if __name__ == "__main__":
    print('Starting tcp client container...')
    tcp_client_container = TcpClientContainer()