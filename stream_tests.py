import os
import sys
import json
import unittest
import stream
import random
import logging
from stream import MergedStream, MergedStreamManager, Stream, valid_stream_name
from mock import Mock

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

log = logging.getLogger("jleung.peloton.stream_tests")
log.setLevel(logging.DEBUG)
log.addHandler(sh)


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        stream.app.config['TESTING'] = True
        self.app = stream.app.test_client()

        stream.merged_stream_manager = MergedStreamManager()

#        TODO: mock server endpoint
#        self.test_stream1 = [2, 6, 11, 14, 15, 21]
#        self.test_stream2 = [10, 11, 22, 50, 88, 92]

 
    def tearDown(self):
        stream.merged_stream_manager = None


    def test_stream(self):
        stream_name = "stream{0}".format(random.randint(1, 10000))
        stream = Stream(stream_name)
        assert stream.stream_name == stream_name
        assert stream.stream_uri == "https://api.pelotoncycle.com/quiz/next/{0}".format(stream_name)


    def test_stream_name(self):
        assert valid_stream_name("test") == True
        assert valid_stream_name("@test%") == False 
        assert valid_stream_name("test%") == False 
        assert valid_stream_name("te!st") == False 
        assert valid_stream_name("test ") == False 
        assert valid_stream_name(" test") == False 
        assert valid_stream_name("te st") == False 


    def test_merged_stream(self):
        stream1 = Stream("stream{0}".format(random.randint(1, 10000)))
        stream2 = Stream("stream{0}".format(random.randint(1, 10000)))
        merged_stream = MergedStream(stream1, stream2)

        # grab first element
        current_element = merged_stream.next_element()
        last_element = current_element["last"]

        for i in range(0, 9):
            log.debug("current_element: {0}, last_element: {1}".format(current_element["current"], current_element["last"]))
            assert last_element <= current_element["current"]

            current_element = merged_stream.next_element()
            last_element = current_element["current"]


    def test_merge_route(self):
        last_response = self.app.get('quiz/merge/?stream1=test1&stream2=test2')
        last_response_data = json.loads(last_response.data)

        assert last_response.status_code == 200

        for i in range(0, 9):
            current_response = self.app.get('quiz/merge/?stream1=test1&stream2=test2')
            current_response_data = json.loads(current_response.data)

            assert current_response.status_code == 200
            assert last_response_data["current"] <= current_response_data["current"]

            last_reponse_data = current_response_data


if __name__ == '__main__':
    unittest.main()

