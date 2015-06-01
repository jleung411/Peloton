import requests 
import json
import sys
import re
import traceback
import logging

from flask import Flask, request, jsonify
app = Flask(__name__)


sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

log = logging.getLogger("jleung.peloton.stream")
log.setLevel(logging.DEBUG)
log.addHandler(sh)


class Stream:

    SERVER_ENDPOINT_URI = "https://api.pelotoncycle.com/quiz/next/"

    def __init__(self, stream_name):
        self.stream_name = stream_name
        self.stream_uri = self.SERVER_ENDPOINT_URI + self.stream_name

    def next_element(self):
        # return -1 if anything goes wrong
        data = {"last": -1, "current": -1, "stream": ""}

        try:
            response = requests.get(self.stream_uri)
            data = response.json()
        except:
            traceback.print_exc()

        return data


class MergedStream:

    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2

        self.stream1_current_element = self.stream1.next_element()
        self.stream2_current_element = self.stream2.next_element()

        if self.stream1_current_element["current"] < self.stream2_current_element["current"]:
            self.last_element = self.stream1_current_element["last"]
        else:
            self.last_element = self.stream2_current_element["last"]

        log.debug("MergedStream::__init__()")
        log.debug("stream1: {0}, stream2: {1}".format(stream1.stream_name, stream2.stream_name))
        log.debug("stream1_current_element: {0}, stream2_current_element: {1}".format(self.stream1_current_element["current"], self.stream2_current_element["current"]))


    def next_element(self):
        # return -1 if anything goes wrong
        next_element = {"last": -1, "current": -1}

        log.debug("MergedStream::next_element()")
        log.debug("stream1_current_element: {0}, stream2_current_element: {1}".format(self.stream1_current_element["current"], self.stream2_current_element["current"]))

        try:
            if self.stream1_current_element["current"] < self.stream2_current_element["current"]:
                next_element["current"] = self.stream1_current_element["current"]
                self.stream1_current_element = self.stream1.next_element()
                log.debug("element: {0}".format(self.stream1_current_element))
            else:
                next_element["current"] = self.stream2_current_element["current"]
                self.stream2_current_element = self.stream2.next_element()
                log.debug("element: {0}".format(self.stream2_current_element))

            next_element["last"] = self.last_element
            self.last_element = next_element["current"]
        except:
            traceback.print_exc()

        return next_element


# For simplicity, this class only manages one merged stream
class MergedStreamManager:

    def __init__(self):
        self.merged_stream = None

    # This merged_stream singleton is not thread safe
    def get_instance(self, stream1, stream2):
        if self.merged_stream is None:
            self.merged_stream = MergedStream(stream1, stream2)
        return self.merged_stream


merged_stream_manager = MergedStreamManager()


def valid_stream_name(stream_name):
    return True if re.match("^[A-Za-z0-9_-]*$", stream_name) else False


@app.route("/quiz/merge/")
def merge():
    # return -1 if anything goes wrong
    response = {"last": -1, "current": -1} 

    try:
        stream_name1 = request.args.get("stream1")
        stream_name2 = request.args.get("stream2")

        if valid_stream_name(stream_name1) and valid_stream_name(stream_name2):
            stream1 = Stream(stream_name1)
            stream2 = Stream(stream_name2)

            merged_stream = merged_stream_manager.get_instance(stream1, stream2)
            response = merged_stream.next_element()
        else:
            raise Exception("Invalid stream name supplied")
    except:
        traceback.print_exc()
        # return some useful information for debugging
        response["exception"] = traceback.format_exc()

    return jsonify(**response)


@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()


