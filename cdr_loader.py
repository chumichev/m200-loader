# -*- coding: utf-8 -*-
import logging
import sys
from m200_collector import M200Collector
from multiprocessing import Queue


def main():
    cdr_queue = Queue()
    online_collector = M200Collector(host='10.90.254.116', port=20002, output_queue=cdr_queue)
    online_collector.start()

    while True:
        # TODO: Разобраться с выходом из цикла если процесс мёртв
        if not online_collector.is_alive():
            break
        cdr = cdr_queue.get()
        print(cdr)

    online_collector.join()


if __name__ == '__main__':
    main()
