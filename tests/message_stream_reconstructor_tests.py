import unittest
from message_stream_reconstructor import MessageStreamReconstructor

class MessageStreamReconstructorTests(unittest.TestCase):
    def test_reconstruct_stream_messages(self):
        message_stream_reconstructor = MessageStreamReconstructor()
        #Reconstruct a full message
        message_bytes = b'\n\x08test key"\x0bTest string*\x0c\x08\x80\x88\xbe\x89\x06\x10\x80\xcb\xec\x9e\x03'
        message_bytes_with_prepend = message_stream_reconstructor.construct_payload_message(message_bytes)
    
        expected_reconstructed_payloads = [message_bytes]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend, expected_reconstructed_payloads)
        #-------------------------------------------------------------------
        #Only got a part of the output, no output expected
        message_bytes = b'\n\x08test key"\x0bTest string*\x0c\x08\x80\x88\xbe\x89\x06\x10\x80\xcb\xec\x9e\x03'
        message_bytes_with_prepend = message_stream_reconstructor.construct_payload_message(message_bytes)

        expected_reconstructed_payloads = []

        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[:20], expected_reconstructed_payloads)

        #Add the missing part
        expected_reconstructed_payloads = [message_bytes]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[20:], expected_reconstructed_payloads)
        #-------------------------------------------------------------------
        #Two messages split up in 4 packets
        message_bytes_1 = b'\n\x08test key"\x0bTest string*\x0c\x08\x80\x88\xbe\x89\x06\x10\x80\xcb\xec\x9e\x03'
        message_bytes_with_prepend_1 = message_stream_reconstructor.construct_payload_message(message_bytes_1)
    
        message_bytes_2 = b'\n\x0eSome other key"\x11Some other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend_2 = message_stream_reconstructor.construct_payload_message(message_bytes_2)
        message_bytes_with_prepend_total = message_bytes_with_prepend_1 + message_bytes_with_prepend_2

        expected_reconstructed_payloads = []
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend_total[:10], expected_reconstructed_payloads)

        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend_total[10:15], expected_reconstructed_payloads)
         
        #first message should appear now
        expected_reconstructed_payloads = [message_bytes_1]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend_total[15:45], expected_reconstructed_payloads)
        
        expected_reconstructed_payloads = [message_bytes_2]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend_total[45:], expected_reconstructed_payloads)


        #-------------------------------------------------------------------
        #3 messages in one packet
        message_bytes_1 = b'\n\x08test key"\x0bTest string*\x0c\x08\x80\x88\xbe\x89\x06\x10\x80\xcb\xec\x9e\x03'
        message_bytes_with_prepend = message_stream_reconstructor.construct_payload_message(message_bytes_1)

        message_bytes_2 = b'\n\x0eSome other key"\x11Some other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend += message_stream_reconstructor.construct_payload_message(message_bytes_2)

        message_bytes_3 = b'\n\x0eYet another key"\x11Yet other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend += message_stream_reconstructor.construct_payload_message(message_bytes_3)

        expected_reconstructed_payloads = [message_bytes_1, message_bytes_2, message_bytes_3]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend, expected_reconstructed_payloads)

        #-------------------------------------------------------------------
        #3messages in 3 packets, the payload header is split over packets
        message_bytes_1 = b'\n\x08test key"\x0bTest string*\x0c\x08\x80\x88\xbe\x89\x06\x10\x80\xcb\xec\x9e\x03'
        message_bytes_with_prepend = message_stream_reconstructor.construct_payload_message(message_bytes_1)

        message_bytes_2 = b'\n\x0eSome other key"\x11Some other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend += message_stream_reconstructor.construct_payload_message(message_bytes_2)

        message_bytes_3 = b'\n\x0eYet another key"\x11Yet other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend += message_stream_reconstructor.construct_payload_message(message_bytes_3)

        #First message should be decoded here
        expected_reconstructed_payloads = [message_bytes_1]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[:42], expected_reconstructed_payloads)
        expected_reconstructed_payloads = [message_bytes_2]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[42:95], expected_reconstructed_payloads)

        expected_reconstructed_payloads = [message_bytes_3]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[95:], expected_reconstructed_payloads)
        

        #-------------------------------------------------------------------
        #3messages in 3 packets, the payload header is split over packets, 2nd packet just contains 1 header byte
        message_bytes_1 = b'\n\x08test key"\x0bTest string*\x0c\x08\x80\x88\xbe\x89\x06\x10\x80\xcb\xec\x9e\x03'
        message_bytes_with_prepend = message_stream_reconstructor.construct_payload_message(message_bytes_1)

        message_bytes_2 = b'\n\x0eSome other key"\x11Some other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend += message_stream_reconstructor.construct_payload_message(message_bytes_2)

        message_bytes_3 = b'\n\x0eYet another key"\x11Yet other string*\x0c\x08\xae\xd6\xbe\x89\x06\x10\x80\x8b\xdf\xe7\x01'
        message_bytes_with_prepend += message_stream_reconstructor.construct_payload_message(message_bytes_3)

        #First message should be decoded here
        expected_reconstructed_payloads = [message_bytes_1]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[:42], expected_reconstructed_payloads)
        expected_reconstructed_payloads = []
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[42:43], expected_reconstructed_payloads)

        expected_reconstructed_payloads = [message_bytes_2, message_bytes_3]
        self.__run_partial_test_case(message_stream_reconstructor, message_bytes_with_prepend[43:], expected_reconstructed_payloads)


    def __run_partial_test_case(self, message_stream_reconstructor, message_bytes, expected_reconstructed_payloads):
        reconstructed_messages = message_stream_reconstructor.reconstruct_stream_messages(message_bytes)
        # print(f'expected output: {expected_reconstructed_payloads}')
        # print(f'reconstructed message: {reconstructed_messages}')
        #Make sure that the payload lists have the same length
        self.assertEqual(len(reconstructed_messages), len(expected_reconstructed_payloads))
        for idx, expected_payload in enumerate(expected_reconstructed_payloads):
            self.assertEqual(reconstructed_messages[idx], expected_payload)

if __name__ == '__main__':
    unittest.main()
