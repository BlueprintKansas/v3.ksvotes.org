# -*- coding: utf-8 -*-
from django.db import connection
import datetime


class RegistrantStats:
    def vr_total_processed(self):
        sql = (
            "select count(id) from ksvotes_registrant where vr_completed_at is not null"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            r = cursor.fetchone()
            return r[0]

    def ab_total_processed(self):
        sql = (
            "select count(id) from ksvotes_registrant where ab_completed_at is not null"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            r = cursor.fetchone()
            return r[0]

    def vr_through_today(self, start_date, end_date=None):
        today = datetime.date.today() + datetime.timedelta(days=1)
        if not end_date:
            end_date = today
        sql = """
      select cast(vr_completed_at at time zone 'utc' at time zone 'america/chicago' as date) as vr_date, count(id)
      from ksvotes_registrant
      where vr_completed_at is not null and vr_completed_at at time zone 'utc' at time zone 'america/chicago' between %s and %s
      group by vr_date
      order by 1
    """
        with connection.cursor() as cursor:
            cursor.execute(sql, [start_date, end_date])
            return cursor.fetchall()

    def ab_through_today(self, start_date, end_date=None):
        today = datetime.date.today() + datetime.timedelta(days=1)
        if not end_date:
            end_date = today
        sql = """
      select cast(ab_completed_at at time zone 'utc' at time zone 'america/chicago' as date) as ab_date, count(id)
      from ksvotes_registrant
      where ab_completed_at is not null and ab_completed_at at time zone 'utc' at time zone 'america/chicago' between %s and %s
      group by ab_date
      order by 1
    """
        with connection.cursor() as cursor:
            cursor.execute(sql, [start_date, end_date])
            return cursor.fetchall()

    def reg_lookups(self, start_date, end_date=None):
        today = datetime.date.today() + datetime.timedelta(days=1)
        if not end_date:
            end_date = today
        sql = """
      select cast(created_at at time zone 'utc' at time zone 'america/chicago' as date) as lookup_date, count(id)
      from ksvotes_registrant
      where reg_lookup_complete is true and created_at at time zone 'utc' at time zone 'america/chicago' between %s and %s
      group by lookup_date
      order by 1
    """
        with connection.cursor() as cursor:
            cursor.execute(sql, [start_date, end_date])
            return cursor.fetchall()

    def reg_lookups_successful(self, start_date, end_date=None):
        today = datetime.date.today() + datetime.timedelta(days=1)
        if not end_date:
            end_date = today
        sql = """
      select cast(created_at at time zone 'utc' at time zone 'america/chicago' as date) as lookup_date, count(id)
      from ksvotes_registrant
      where reg_found is true and created_at at time zone 'utc' at time zone 'america/chicago' between %s and %s
      group by lookup_date
      order by 1
    """
        with connection.cursor() as cursor:
            cursor.execute(sql, [start_date, end_date])
            return cursor.fetchall()
