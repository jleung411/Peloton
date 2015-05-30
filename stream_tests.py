import os
import unittest
import stream
from stream import MergedStream, MergedStreamManager, Stream, valid_stream_name
from mock import Mock


class FlaskrTestCase(unittest.TestCase):


    def setUp(self):
        stream.app.config['TESTING'] = True
        self.app = stream.app.test_client()
        self.stream1 = [2, 6, 11, 14, 15, 21]
        self.stream2 = [10, 11, 22, 50, 88, 92]

 
#    def tearDown(self):


    def test_stream(self):
        stream1 = Stream("stream1")
        assert stream1.stream_name == "stream1"
        assert stream1.stream_uri == "https://api.pelotoncycle.com/quiz/next/stream1"


    def test_stream_name(self):
        assert valid_stream_name("test") == True
        assert valid_stream_name("@test%") == False 
        assert valid_stream_name("test%") == False 
        assert valid_stream_name("te!st") == False 
        assert valid_stream_name("test ") == False 
        assert valid_stream_name(" test") == False 
        assert valid_stream_name("te st") == False 


    def test_merged_stream(self):
        stream1 = Stream("stream1")
        stream1.next_element = Mock(return_value={"last": 2, "current": 6})

        stream2 = Stream("stream2")
        stream2.next_element = Mock(return_value={"last": 10, "current": 11})

        merged_stream = MergedStream(stream1, stream2)

        # grab first element
        current_element = merged_stream.next_element()
        last_element = current_element["last"]

        for i in range(0, 3): 
#            print "last_element: {0}".format(last_element)
            print "current_element: {0} ".format(current_element["current"])

            assert last_element <= current_element["current"]

            current_element = merged_stream.next_element()
            last_element = current_element["current"]

        next_element = merged_stream.next_element()
        print next_element


    def test_merge_route(self):
        stream.merged_stream_manager = MergedStreamManager()
        response = self.app.get('quiz/merge/?stream1=test1&stream2=test2')
        assert response.status_code == 200

if __name__ == '__main__':
    unittest.main()

