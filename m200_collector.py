# -*- coding: utf-8 -*-

import socket
import logging
from multiprocessing import Process, Queue
from time import sleep


class M200Collector(Process):

    CONNECTION_TIMEOUT = 5

    def __init__(self, host: str, port: int, output_queue: Queue, collector_id: str,
                 buffer_size=1024, encoding='cp1251', reconnect_timeout=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = collector_id
        self._buffer_size = buffer_size
        self._encoding = encoding
        self._output_queue = output_queue
        self._m200_address = (host, port)
        self._tcp_socket = None
        self._connected = False
        self._reconnect_timeout = reconnect_timeout

    def _setup_socket(self) -> None:
        """
        Установка параметров сокета (без подключения)
        """
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.settimeout(self.CONNECTION_TIMEOUT)
        if hasattr(socket, 'SO_KEEPALIVE'):
            # включение функционала tcp keepalive чтобы соединение не закрывалось
            # по причине долгого отсутствия данных по ночам
            self._tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, 'TCP_KEEPIDLE'):
            # шлёт keepalive после 20 секунд бездействия
            self._tcp_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 20)
        if hasattr(socket, 'TCP_KEEPINTVL'):
            # интервал отправки keepalive 5 секунд
            self._tcp_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)

    def _connect(self) -> None:
        """
        Подключает сокет на адрес и порт переданные в _m200_address
        """
        self._setup_socket()
        self._tcp_socket.connect(self._m200_address)
        self._tcp_socket.settimeout(None)
        self._connected = True
        print(f"[{self.id}] {self._m200_address} PID {self.pid} Connected!", flush=True)
        logging.info(f"[{self.id}] PID {self.pid} Connected!")

    def run(self) -> None:
        try:
            self._connect()
        except socket.error:
            logging.exception(f"[{self.id}] {self._m200_address} PID {self.pid} "
                              f"Error while connecting to {self._m200_address}")
            self._tcp_socket.close()
            self.terminate()

        while True:
            try:
                data = self._tcp_socket.recv(self._buffer_size)
                if data:
                    raw_cdr = data.decode(encoding=self._encoding).lstrip('\x02').strip()
                    self._output_queue.put((self.id, raw_cdr))
            except socket.error:
                # потеря соединения, пишем информацию в лог и пытаемся переподключиться
                host, port = self._m200_address
                message = f"[{self.id}] Connection to {host}:{port} lost. Reconnecting..."
                logging.debug(message)
                self._connected = False
                # попытки переподключения до тех пор пока связь не восстановится
                while not self._connected:
                    try:
                        self._setup_socket()
                        self._tcp_socket.connect(self._m200_address)
                        self._tcp_socket.settimeout(None)
                        self._connected = True
                        message = f"[{self.id}] PID {self.pid} Reconnected to {host}:{port} successfully!"
                        logging.debug(message)
                    except socket.error:
                        # ждём таймаут и снова пытаемся переподключиться
                        sleep(self._reconnect_timeout)
            except KeyboardInterrupt:
                self._tcp_socket.close()
                print(f"[{self.id}] {self._m200_address} PID {self.pid} Connection closed")
                self.terminate()
            except Exception:
                logging.exception(f"[{self.id}] PID {self.pid} Unexpected error occurred!")
                continue
