# -*- coding: utf-8 -*-

import socket
import logging
from multiprocessing import Process, Queue
from time import sleep


class M200Collector(Process):

    def __init__(self, host: str, port: int, output_queue: Queue,
                 buffer_size=1024, encoding='cp1251', reconnect_timeout=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer_size = buffer_size
        self.encoding = encoding
        self.output_queue = output_queue
        self.m200_address = (host, port)
        self.tcp_socket = None
        self.__connected = False
        self.reconnect_timeout = reconnect_timeout

    def connect(self):
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect(self.m200_address)
            self.__connected = True
        except socket.error as exc:
            host, port = self.m200_address
            message = f"Cannot open connection to {host}:{port} - {exc}"
            logging.critical(message)
            raise IOError(message)

    def run(self) -> None:
        self.connect()
        while True:
            try:
                data = self.tcp_socket.recv(self.buffer_size)
                if data:
                    raw_cdr = data.decode(encoding=self.encoding).strip()
                    self.output_queue.put(raw_cdr)
            except socket.error:
                host, port = self.m200_address
                message = f"Connection to {host}:{port} lost. Reconnecting..."
                logging.debug(message)
                self.__connected = False
                self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                while not self.__connected:
                    try:
                        self.tcp_socket.connect(self.m200_address)
                        self.__connected = True
                        message = f"Reconnected to {host}:{port} successfully!"
                        logging.debug(message)
                    except socket.error:
                        sleep(self.reconnect_timeout)
