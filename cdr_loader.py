# -*- coding: utf-8 -*-

import argparse
import logging
import queue
from m200_collector import M200Collector
from multiprocessing import Queue


def start_cdr_collection(host: str, port: int) -> None:
    cdr_queue = Queue()
    online_collector = M200Collector(host=host, port=port, output_queue=cdr_queue)
    online_collector.start()

    while online_collector.is_alive():
        try:
            cdr = cdr_queue.get(timeout=1)
            print(cdr)
        except queue.Empty:
            # Здесь ничего не нужно делать. Очередь пустая? - проверяем жив ли процесс коллектор.
            # Если жив, то снова ждём очередь и так по кругу. Если коллектор умер, то завершаем приложение
            continue

    online_collector.join()


if __name__ == '__main__':

    # Запуск (пример): cdr_loader.py --host 192.168.0.100 --port 20002

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help='IP-адрес хоста с запущенным SMPCallBuilder')
    parser.add_argument('--port', type=int, required=True, help='Порт SMPCallBuilder')
    args = parser.parse_args()

    start_cdr_collection(host=args.host, port=args.port)
