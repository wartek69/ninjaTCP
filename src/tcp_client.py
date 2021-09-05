#!/usr/bin/env python3
from queue import Queue
import socket
from pubsub import pub

from threading import Thread
import time
from message_stream_reconstructor import MessageStreamReconstructor

class HeartbeatManager:
    def __init__(self):
        #give some time for initialisation of the sockets
        self.last_heartbeat = time.time() + 1
    
    def update_heartbeat(self):
        self.last_heartbeat = time.time()

    def check_heartbeat_alive(self):

        """Returns true if a heartbeat has been received recently, else False
        """
        return time.time() - self.last_heartbeat < 3


class TcpClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None
        self.message_stream_reconstructor = MessageStreamReconstructor()
        self.heartbeat_manager = HeartbeatManager()
        self.is_alive = True
        self.amount_of_messages_received_sec = 0
        self.amount_of_messages_send_sec = 0
        self.connect_to_server()
        self.thread = Thread(target = self.receive_messages)
        self.thread.daemon = True
        self.thread.start()
        self.last_throughput_metric_update = time.time()
        self.hb_thread = Thread(target = self.heartbeat_loop)
        self.hb_thread.daemon = True
        self.hb_thread.start()
        self.received_messages_buffer = Queue()

    def heartbeat_loop(self):
        while self.is_alive:
            if not self.heartbeat_manager.check_heartbeat_alive():
                #Send a reconnection signal to the outside so that this object gets disposed and reinitialised
                print('Lost the heartbeat, sending a request to reinit the tcp client!')
                pub.sendMessage('reconnect_tcp_client')
                break
            time.sleep(0.1)

    def connect_to_server(self):
        try:
            print(f'Connecting to {self.ip}:{self.port}')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            pass

    def receive_messages(self):
        while self.is_alive:
            try:
                data = self.socket.recv(8192)
                if data == b'':
                    print(f'Connection loss detected!')
                    time.sleep(1)
                else:
                    reconstructed_messages = self.message_stream_reconstructor.reconstruct_stream_messages(data)
                    self.heartbeat_manager.update_heartbeat()
                    for message in reconstructed_messages:
                        self.amount_of_messages_received_sec += 1
                        self.received_messages_buffer.put(message)

                    elapsed_time = time.time() - self.last_throughput_metric_update
                    if  elapsed_time > 1:
                        message_per_sec_str = f'received: {self.amount_of_messages_received_sec}, send: {self.amount_of_messages_send_sec} messages in {elapsed_time:.2f} sec'
                        print(message_per_sec_str)
                        self.amount_of_messages_received_sec = 0
                        self.amount_of_messages_send_sec = 0
                        self.last_throughput_metric_update = time.time()
            except OSError:
                pass
                #print("Cannot receive, no socket is connected")
            except Exception as e:
                pub.sendMessage('error_handler', e)


    def send_data(self, data_bytes):
        """Prepends the message byte length to the bytes and sends these bytes over the tcp socket.

        Args:
            data_bytes (str): a byte string containing the bytes that need to be send over the tcp socket
        """
        try:
            data_bytes_with_header = self.message_stream_reconstructor.construct_payload_message(data_bytes)
            self.socket.sendall(data_bytes_with_header)
            self.amount_of_messages_send_sec += 1
        except BrokenPipeError as e:
            print('Cannot send data, not connected to a server!')
        except OSError:
            print('Cannot send data, not connected to a server!')

    
    def dispose(self):
        """Clean shutdown of the tcp client
        """
        print('Disposing tcp client!')
        self.is_alive = False
        self.socket.close()




