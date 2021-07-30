# -*- coding: utf-8 -*-
from datetime import datetime


# специальный класс исключений для проброса ошибок тарификации по стеку
class BillingError(Exception):

    def __init__(self, err_code: int, raw_cdr: str, err_message=''):
        self.err_code = err_code
        self.err_message = err_message
        self.raw_cdr = raw_cdr


class UnexpectedBillingError(BillingError):

    def __init__(self, raw_cdr, message):
        super().__init__(err_code=6, raw_cdr=raw_cdr, err_message=message)


class CDR:

    def __init__(self, raw_cdr):
        self._raw_cdr = raw_cdr
        # self._logger = logger

    def parse_raw_cdr(self) -> dict:
        try:
            cg_trunk, cg_num, cd_trunk, cd_num, raw_date, raw_time, call_length, end_cause = self._raw_cdr.split()
            call_length = int(call_length)
            end_cause = int(end_cause)
            c_time = datetime.strptime(raw_time, '%H:%M:%S')
            c_date = datetime.strptime(raw_date, '%d-%m-%y')
            c_start_moment = datetime(year=c_date.year, month=c_date.month, day=c_date.day,
                                      hour=c_time.hour, minute=c_time.minute, second=c_time.second)

            return {
                'cg_trunk': cg_trunk,
                'aon': cg_num,
                'cd_trunk': cd_trunk,
                'number': cd_num,
                'c_start_moment': c_start_moment,
                'call_length': call_length,
                'end_cause': end_cause,
                'src_hash': abs(hash(self._raw_cdr)),
                'src_string': self._raw_cdr,
            }
        except (IndexError, ValueError) as exc:
            message = f'Неверный формат строки "{self._raw_cdr}": {exc}'
            # self._logger.error(message)
            raise UnexpectedBillingError(raw_cdr=self._raw_cdr, message=message)
