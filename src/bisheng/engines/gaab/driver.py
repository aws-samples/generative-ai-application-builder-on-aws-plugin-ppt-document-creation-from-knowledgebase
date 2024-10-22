# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import queue
import re
import threading

import websocket

from bisheng.engines.gaab.response import GaabResponse
from bisheng.engines.websocket_engine import WebSocketEngine
from bisheng.prompting.base_prompt import BasePrompt

_ACTION_NAME = 'sendMessage'
_STOP_TOKEN = '##END_CONVERSATION##'
_CONNECTION_OPEN_TIMEOUT = 5


def check_for_specific_message(message):
    return message["data"] == _STOP_TOKEN


class GaabStreamingEngine(WebSocketEngine):

    def __init__(self, ws_url: str, **kwargs):
        super().__init__(**kwargs)
        self.ws = None
        self.is_connected = False
        self.ws_url = f"{ws_url}?Authorization={self.token}"
        self.message_queue = queue.Queue()
        self.responses = []
        self.event = threading.Event()
        self.is_connected = threading.Event()

    def connect(self):
        self.ws = websocket.WebSocketApp(self.ws_url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def on_open(self, ws):
        print("WebSocket connection opened")
        self.is_connected.wait(_CONNECTION_OPEN_TIMEOUT)
        self.is_connected.set()
        # self.send_queued_messages()

    def on_error(self, ws, error):
        print(f"Error occurred: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket connection closed with code {close_status_code}")
        print(f"WebSocket connection closed with message {close_msg}")
        self.is_connected = False

    def on_message(self, ws, message):
        print("Received message:", message)
        if "data" in json.loads(message).keys():
            message = json.loads(message)
            if check_for_specific_message(message):
                self.event.set()
            else:
                self.message_queue.put(message["data"])
        elif "sourceDocument" in json.loads(message).keys():
            self.message_queue.put(message)
        elif "generated_question" in json.loads(message).keys():
            message = json.loads(message)
            self.message_queue.put(message["generated_question"])

    def wait_for_specific_message(self):
        self.event.wait()
        self.event.clear()

    def get_messages(self):
        messages = []
        current_word = ""

        while not self.message_queue.empty():
            token = self.message_queue.get()
            if isinstance(token, str) and token.startswith(" "):
                if current_word:
                    messages.append(current_word)
                    current_word = ""
                current_word += token.strip()
            else:
                current_word += token

        if current_word:
            messages.append(current_word)

        return messages

    def invoke(self, prompt: BasePrompt):
        request_body = {
            "action": _ACTION_NAME,
            "question": prompt.get_instruction_prompt(),
            "authToken": self.token,
            "conversationId": "",
            "promptTemplate": prompt.get_system_prompt() + "\n\n{context}\n\n{history}\n\n{input}",
        }

        if not self.is_connected.is_set():
            self.wait_for_connection(5)
        self.ws.send(json.dumps(request_body))
        print(f"Sent message: {request_body}")
        rationale_matches, response_matches, source_matches = self.process_response()
        return GaabResponse(
            rationale=rationale_matches[0] if len(rationale_matches) > 0 else "",
            response=response_matches[0] if len(response_matches) > 0 else "",
            sources=source_matches[0] if len(source_matches) > 0 else ""
        )

    def process_response(self):
        self.wait_for_specific_message()
        message = (" ".join(self.get_messages()))
        print(message)
        rationale_regex = r"<rationale>(.*)</rationale>"
        response_regex = r"<response>(.*)</response>"
        source_regex = r"({\"sourceDocument\":.*)INPUT DATA"
        rationale_matches = re.findall(rationale_regex, message, re.DOTALL)
        response_matches = re.findall(response_regex, message, re.DOTALL)
        source_matches = re.findall(source_regex, message, re.DOTALL)
        return rationale_matches, response_matches, source_matches

    def wait_for_connection(self, timeout=None):
        return self.is_connected.wait(timeout)
