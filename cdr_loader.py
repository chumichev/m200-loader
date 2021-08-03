# -*- coding: utf-8 -*-
import datetime
import logging
import os
import os.path
import queue
import sys
import psycopg2
from m200_collector import M200Collector
from cdr_worker import CDR, BillingError
from multiprocessing import Queue

try:
    import settings
except ImportError:
    logging.error('Не найден файл settings.py\nВыполните mv settings.default.py settings.py и проверьте конфигурацию')
    sys.exit(1)

cdr_collectors = []


def build_db_dsn():
    return f"host={settings.db_host} " \
           f"user={settings.db_user} " \
           f"password={settings.db_password} " \
           f"dbname={settings.db_name}"


def get_db_connection():
    try:
        conn = psycopg2.connect(dsn=build_db_dsn())
        return conn
    except psycopg2.OperationalError:
        logging.exception('Ошибка подключения к базе данных')
        sys.exit(1)


def reconnect_to_db(current_conn, retry_count=2):
    reconnect_retry = 0
    while reconnect_retry < retry_count:
        try:
            conn = psycopg2.connect(dsn=build_db_dsn())
            return conn, True
        except psycopg2.OperationalError:
            reconnect_retry += 1
            print(f'Потеряно подключение к БД. Попытка переподключения {reconnect_retry}...')

    return current_conn, False


def get_err_file_path(collector_id: str) -> str:
    base_path = os.path.abspath(settings.ERRORED_CDR_PATH)
    current_date = datetime.datetime.now()
    file_name = f'{current_date.year}_{current_date.month}_{current_date.day}.log'
    path_to_file = os.path.join(base_path, collector_id)
    if not os.path.exists(path_to_file):
        os.makedirs(path_to_file)
    return os.path.join(path_to_file, file_name)


def save_cdr_to_file(collector_id, cdr):
    file_name = get_err_file_path(collector_id=collector_id)
    with open(file=file_name, mode='a', encoding='utf8') as err_file:
        err_file.write(f'{cdr}\n')


def main() -> None:
    db_connection = get_db_connection()
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
            # Проверка живое ли подключение к БД
            if db_connection.closed:
                db_connection, reconnect_success = reconnect_to_db(current_conn=db_connection)
                if not reconnect_success:
                    logging.warning('Не удалось восстановить подключение к БД. Строка CDR будет сохранена в файл!')
                    save_cdr_to_file(collector_id, cdr)
                    print(f"'--->'\t{cdr}")
                    continue
            cdr_object = CDR(raw_cdr=cdr, db=db_connection, src=collector_id)
            cdr_object.save_to_db()
            print(f"{collector_id}\t{cdr}")
        except queue.Empty:
            # Здесь ничего не нужно делать. Очередь пустая? - проверяем жив ли хотя бы один коллектор.
            # Если хотя бы один жив, то снова ждём очередь и так по кругу.
            continue
        except BillingError as exc:
            logging.error(exc.err_message)
            save_cdr_to_file(exc.collector_id, exc.raw_cdr)
            continue
        except KeyboardInterrupt:
            for collector in cdr_collectors:
                collector.terminate()
            break

    # Если ни одного коллектора не осталось - синхронизируемся и завершаем работу
    for collector in cdr_collectors:
        collector.join()


if __name__ == '__main__':
    main()
