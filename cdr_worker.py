# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import pytz


# специальный класс исключений для проброса ошибок тарификации по стеку
class BillingError(Exception):

    def __init__(self, err_code: int, raw_cdr: str, collector_id='', err_message=''):
        self.err_code = err_code
        self.err_message = err_message
        self.raw_cdr = raw_cdr
        self.collector_id = collector_id


class UnexpectedBillingError(BillingError):

    def __init__(self, raw_cdr, collector_id, message):
        super().__init__(err_code=6, raw_cdr=raw_cdr, collector_id=collector_id, err_message=message)


class CDR:

    def __init__(self, raw_cdr: str, src: str, db) -> None:
        self._raw_cdr = raw_cdr.lstrip('\x02')
        # self._logger = logger
        self.cg_trunk = str
        self.cg_num = str
        self.cd_num = str
        self.cd_trunk = str
        self.raw_date = str
        self.raw_time = str
        self.call_length = int
        self.call_length_total = None
        self.end_cause = int
        self.cg_num_t = None
        self.cd_num_t = None
        self.c_start_moment = None
        self._cdr_data = None
        self.db_conn = db
        self._cdr_source = src

    def _parse_raw_cdr(self):
        # TODO: Вынести это в параметры коллектора
        current_tz = 'Europe/Moscow'

        call_length, end_cause = '0', '0'
        call_length_total = None
        try:
            call_data = self._raw_cdr.split()
            if len(call_data) == 8:
                # формат МР-16 и К86 (без полной продолжительности звонка и преобразованных номеров)
                self.cg_trunk, self.cg_num, self.cd_trunk, self.cd_num, self.raw_date, self.raw_time, \
                    call_length, end_cause = call_data
            elif len(call_data) == 11:
                # формат СС
                self.cg_trunk, self.cg_num, self.cd_num, self.cd_trunk, self.cg_num_t, self.cd_num_t, self.raw_date, \
                    self.raw_time, call_length_total, call_length, end_cause = call_data

            if call_length_total:
                self.call_length_total = int(call_length_total)

            self.call_length = int(call_length)
            self.end_cause = int(end_cause)
            c_time = datetime.strptime(self.raw_time, '%H:%M:%S')
            c_date = datetime.strptime(self.raw_date, '%d-%m-%y')
            self.c_start_moment = pytz.timezone(current_tz).localize(
                datetime(year=c_date.year, month=c_date.month, day=c_date.day,
                         hour=c_time.hour, minute=c_time.minute, second=c_time.second),
                is_dst=None)

            self._cdr_data = (
                self.cg_trunk,
                self.cg_num,
                self.cg_num_t,
                self.cd_trunk,
                self.cd_num,
                self.cd_num_t,
                self.c_start_moment,
                self.call_length_total,
                self.call_length,
                self.end_cause,
                abs(hash(self._raw_cdr)),
                self._raw_cdr,
                self._cdr_source,
            )

        except (IndexError, ValueError) as exc:
            message = f'Неверный формат строки "{self._raw_cdr}": {exc}'
            # self._logger.error(message)
            raise UnexpectedBillingError(raw_cdr=self._raw_cdr, message=message, collector_id=self._cdr_source)
        except Exception as exc:
            message = f'Непредвиденная ошибка при обработке строки "{self._raw_cdr}": {exc}'
            # self._logger.error(message)
            raise UnexpectedBillingError(raw_cdr=self._raw_cdr, message=message, collector_id=self._cdr_source)

    def save_to_db(self):
        self._parse_raw_cdr()
        try:
            sql = "insert into cdrs (cg_trunk, aon, aon_t, cd_trunk, called_number, number_t, c_start_moment, " \
                  "call_length_total, call_length, end_cause, src_hash, src_string, cdr_source) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor = self.db_conn.cursor()
            cursor.execute(sql, self._cdr_data)
            self.db_conn.commit()
        except Exception as exc:
            self.db_conn.rollback()
            message = f'Ошибка записи в БД: "{self._raw_cdr}": {exc}'
            logging.exception(message)
            # self._logger.error(message)
            raise UnexpectedBillingError(raw_cdr=self._raw_cdr, message=message, collector_id=self._cdr_source)
