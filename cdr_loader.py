# -*- coding: utf-8 -*-

import settings
import logging
import queue
from m200_collector import M200Collector
from multiprocessing import Queue

cdr_collectors = []


def main() -> None:
    cdr_queue = Queue()
    # создаём коллектор для каждой АТС
    for host, port, collector_id in settings.collectors:
        online_collector = M200Collector(host=host, port=port, output_queue=cdr_queue, collector_id=collector_id)
        cdr_collectors.append(online_collector)

    for collector in cdr_collectors:
        collector.start()

    while any([collector.is_alive() for collector in cdr_collectors]):
        try:
            cdr = cdr_queue.get(timeout=1)
            print(cdr)
        except queue.Empty:
            # Здесь ничего не нужно делать. Очередь пустая? - проверяем жив ли хотя бы один коллектор.
            # Если хотя бы один жив, то снова ждём очередь и так по кругу.
            continue

    # Если ни одного коллектора не осталось - синхронизируемся и завершаем работу
    for collector in cdr_collectors:
        collector.join()


if __name__ == '__main__':
    main()
