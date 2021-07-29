# -*- coding: utf-8 -*-

import socket
import logging
import sys
from multiprocessing import Process, Queue
from time import sleep


class M200Collector(Process):

    CONNECTION_TIMEOUT = 5

    def __init__(self, host: str, port: int, output_queue: Queue,
                 buffer_size=1024, encoding='cp1251', reconnect_timeout=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer_size = buffer_size
        self._encoding = encoding
        self._output_queue = output_queue
        self._m200_address = (host, port)
        self._tcp_socket = None
        self._connected = False
        self._reconnect_timeout = reconnect_timeout

    def _setup_socket(self):
        """
        Установка параметров сокета (без подключения)
        """
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.settimeout(self.CONNECTION_TIMEOUT)

    def _connect(self):
        """
        Подключает сокет на адрес и порт переданные в _m200_address
        """
        self._setup_socket()
        self._tcp_socket.connect(self._m200_address)
        self._connected = True

    def run(self) -> None:
        try:
            self._connect()
        except socket.error:
            logging.exception(f"Error while connecting to {self._m200_address}")
            sys.exit(0)

        while True:
            try:
                data = self._tcp_socket.recv(self._buffer_size)
                if data:
                    raw_cdr = data.decode(encoding=self._encoding).strip()
                    self._output_queue.put(raw_cdr)
            except socket.error:
                # потеря соединения, пишем информацию в лог и пытаемся переподключиться
                host, port = self._m200_address
                message = f"Connection to {host}:{port} lost. Reconnecting..."
                logging.debug(message)
                self._connected = False
                # попытки переподключений до тех пор пока связь не восстановится
                while not self._connected:
                    try:
                        self._setup_socket()
                        self._tcp_socket.connect(self._m200_address)
                        self._connected = True
                        message = f"Reconnected to {host}:{port} successfully!"
                        logging.debug(message)
                    except socket.error:
                        # ждём таймаут и снова пытаемся переподключиться
                        sleep(self._reconnect_timeout)
