# -*- coding: utf-8 -*-
import logging
import queue
from m200_collector import M200Collector
from multiprocessing import Queue


def main():
    cdr_queue = Queue()
    online_collector = M200Collector(host='10.90.254.115', port=20002, output_queue=cdr_queue)
    online_collector.start()

    while online_collector.is_alive():
        try:
            cdr = cdr_queue.get(timeout=1)
            print(cdr)
        except queue.Empty:
            # Здесь ничего не нужно делать. Очередь пустая? - проверяем жив ли процесс коллектор.
            # Если жив, то снова ждём очередь и так по кругу. Если коллектор умер, то завершаем приложение
            pass

    online_collector.join()


if __name__ == '__main__':
    main()
