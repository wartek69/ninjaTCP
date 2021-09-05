class MessageStreamReconstructor:
    def __init__(self):
        #(bytes buffer, amount of bytes left to read, header buffer)
        self.buffer = (b'', 0, b'')

    def reconstruct_stream_messages(self, message_bytes_stream: str):
        """Takes a stream of bytes and extracts individual packets from it.
        Works by parsing the payload length that is prepended on each payload and then parse the payload based on that
        Args:
            message_bytes_stream (str): a byte string containing the payload bytes, can come from a stream

        Returns:
            list(str): A list containing the extracted payloads as byte strings
        """
        reconstructed_messages = [] 

        while len(message_bytes_stream) != 0:
            if self.buffer[1] == 0:
                total_amount_of_payload_bytes, message_bytes_stream, buffered_header = self.__strip_length_of_message(message_bytes_stream, self.buffer[2])
                if buffered_header != b'':
                    #Could not obtain a full header, it's split up over different packets
                    assert len(self.buffer[0]) == 0, "Buffer was not empty when addig buffered header"
                    assert self.buffer[1] == 0, "Buffer was not empty when adding buffered header"
                    self.buffer = (b'', 0, buffered_header)
                    break
            else:
                total_amount_of_payload_bytes = self.buffer[1]

            payload_bytes_left = total_amount_of_payload_bytes - len(self.buffer[0])
            partial_payload_bytes = self.buffer[0] + message_bytes_stream[:payload_bytes_left]


            message_bytes_stream = message_bytes_stream[payload_bytes_left:]
            len_partial_payload = len(partial_payload_bytes)

            if len_partial_payload == total_amount_of_payload_bytes:
                reconstructed_messages.append(partial_payload_bytes)
                #clear the buffer
                self.buffer = (b'', 0, b'')
            elif len_partial_payload < total_amount_of_payload_bytes:
                self.buffer = (partial_payload_bytes, total_amount_of_payload_bytes, b'')
            elif len_partial_payload > total_amount_of_payload_bytes:
                print('Cannot have a partial payload bigger than amount of payload bytes, check your code!')
        
        return reconstructed_messages
    
    def construct_payload_message(self, message_bytes: str):
        """Takes a bytes string and prepends the length of the payload in hex

        Args:
            message_bytes (str): a byte string containing the payload bytes

        Returns:
            str: the payload byte string with the length of the payload prepended
        """
        return len(message_bytes).to_bytes(4, 'big') + message_bytes

    def __strip_length_of_message(self, message_bytes, buffered_header = b""):
        """Parses the header that contains the payload length and returns the bytes stream with the header stripped.
        If the full header could not be parsed, the buffered header will get returned

        Args:
            message_bytes (str): Stream of bytes (byte string)
            buffered_header (str): The buffered header from previous stream, means that part of the header was in the previous message
            , optional. Defaults to None.

        Returns:
            tuple(int, str, str): returns the length of the payload, the stripped bytes string and the buffered header string
        """
        
        message_bytes = buffered_header + message_bytes
        length_payload_bytes = message_bytes[0:4]

        if len(length_payload_bytes) != 4:
            #The header is split up over different packets
            return None, None, length_payload_bytes
        else:
            buffered_header = b''

        length_payload_int = int.from_bytes(length_payload_bytes, 'big')
        return length_payload_int, message_bytes[4:], buffered_header

