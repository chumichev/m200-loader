# -*- coding: utf-8 -*-

from m200_collector import M200Collector
from multiprocessing import Queue


def main():
    cdr_queue = Queue()
    online_collector = M200Collector(host='10.90.254.115', port=20002, output_queue=cdr_queue)
    online_collector.start()
    while True:
        cdr = cdr_queue.get()
        print(cdr)


if __name__ == '__main__':
    main()