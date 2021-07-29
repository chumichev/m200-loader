# -*- coding: utf-8 -*-

import socket
import logging
import sys
from multiprocessing import Process, Queue
from time import sleep


class M200Collector(Process):

    def __init__(self, host: str, port: int, output_queue: Queue,
                 buffer_size=1024, encoding='cp1251', reconnect_timeout=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__buffer_size = buffer_size
        self.__encoding = encoding
        self.__output_queue = output_queue
        self.__m200_address = (host, port)
        self.__tcp_socket = None
        self.__connected = False
        self.__reconnect_timeout = reconnect_timeout

    def __connect(self):
        self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_socket.connect(self.__m200_address)
        self.__connected = True

    def run(self) -> None:
        try:
            self.__connect()
        except socket.error:
            logging.exception(f"Error while connecting to {self.__m200_address}")
            return

        while True:
            try:
                data = self.__tcp_socket.recv(self.__buffer_size)
                if data:
                    raw_cdr = data.decode(encoding=self.__encoding).strip()
                    self.__output_queue.put(raw_cdr)
            except socket.error:
                host, port = self.__m200_address
                message = f"Connection to {host}:{port} lost. Reconnecting..."
                logging.debug(message)
                self.__connected = False
                self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                while not self.__connected:
                    try:
                        self.__tcp_socket.connect(self.__m200_address)
                        self.__connected = True
                        message = f"Reconnected to {host}:{port} successfully!"
                        logging.debug(message)
                    except socket.error:
                        sleep(self.__reconnect_timeout)
