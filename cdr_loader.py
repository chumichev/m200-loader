# -*- coding: utf-8 -*-

import logging
import queue
import sys
from m200_collector import M200Collector
from cdr_worker import CDR, BillingError
from multiprocessing import Queue

try:
    import settings
except ImportError:
    logging.error('Не найден файл settings.py\nВыполните mv settings.default.py settings.py и проверьте конфигурацию')
    sys.exit(1)

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
            collector_id, cdr = cdr_queue.get(timeout=1)
            cdr_object = CDR(raw_cdr=cdr)
            data = cdr_object.parse_raw_cdr()
            print(collector_id, data)
        except queue.Empty:
            # Здесь ничего не нужно делать. Очередь пустая? - проверяем жив ли хотя бы один коллектор.
            # Если хотя бы один жив, то снова ждём очередь и так по кругу.
            continue
        except BillingError as exc:
            logging.error(exc.err_message)
            # TODO: Строку с ошибкой записать отдельно от остальных
            # print(exc.raw_cdr)
            continue

    # Если ни одного коллектора не осталось - синхронизируемся и завершаем работу
    for collector in cdr_collectors:
        collector.join()


if __name__ == '__main__':
    main()
