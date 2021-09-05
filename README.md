# NinjaTCP
A simple tcp client that contains all the features to be able to send & receive tcp packets without having to worry about the limitations of plain tcp sockets.
- Ensures that tcp receive always returns complete packets.
- Makes sure that an automatic reconnect happens when a tcp connection is lost

## Run test example
The test code in this library can easily be ran by opening a tcp echo server `python3 src/tcp_server_echo.py` and then creating a tcp client `python3 src/tcp_client_container.py`.

## Motivation
### Streaming protocol
Tcp socket programming is widely used in a large amount of different applications. However, many people do not realise that tcp is a streaming protocol, which means that there is no guarantee that the packet you send on one side will be read as one packet on the other side. Especially when there is an unstable connection or a high throughput of messages is necessary the bytes of the packets will be spread over different buffer reads. For example, if you send the message `b'Hello world'` multiple times, it might be that on the receive side you'll start reading from a single buffer stuff like `b'Hello worldHe'` and the following buffer read will give you `llo world`.
Additional logic is needed to make sure that these messages are read correctly, and this is the aim of this small library.

### Connection loss
Using plain tcp sockets it's quite hard to notice that a connection has been lost without an implementation of some kind of heartbeating mechanism.
There are scenarios where the tcp sockets will throw an error on send/receive when the connection is closed gracefully. But in some cases (for example when you just pull out your ethernet cable) it might be that the underlying os sockets do not realise that the connection is been lost and thus there is a hanging sockets. These issues are easily solved by using heartbeats. In the tcp client implementation found in this repository the heartbeating is done by expecting **any** message during 3 second, if that's not the case the tcp client gets disposed and a new tcp client gets initialised.
The reason for the full disposing of the TcpClient object is to make sure that we do not get into a hell of state management of an object.

## Implementation packet restructuring
The implementation is fairly simple, on each message send a 'header' containing the amount of bytes gets prepended to the message. On the receive side this 'header' is first read to see how many bytes need to be read. After the specified amount of bytes is read, the new header is read and the whole process continues. If the amount of bytes that are specified in the header are not inside the buffer, the current received bytes gets buffered and on next socket read these bytes gets prepended to the newly read bytes.
This logic is implemented in `message_stream_reconstructor.py` and tested in `message_stream_reconstructor_tests`

## Usage in your own code
The `tcp_client_container.py` file contains an example on how to initialise and use the `TcpClient`. There you can see how the events that are thrown by the `TcpClient` are subscribed to handle errors and reconnect the `TcpClient`, more specifically.
```
    pub.subscribe(self.__reconnect_tcpclient, 'reconnect_tcp_client')
    pub.subscribe(self.__handle_tcp_client_errors, 'error_handler')
```
An example on how to receive messages is also provided.
```
    message_bytes = self.tcp_client.received_messages_buffer.get(block=False)
```

### Used libraries
To propagate events the following library is used:
https://github.com/schollii/pypubsub

### Tcp server
Right now only a tcp client that makes use of the `message_stream_reconstructor` is provided. It's straightforward to utilise this class in the TcpServer to make sure that all the messages send & received can read and create messages used by this library.


