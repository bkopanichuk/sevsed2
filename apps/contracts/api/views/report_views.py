from __future__ import unicode_literals

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def contract_summary_data(request):
    sql = """select json_agg(row_to_json(qq)) from (select month_contract, (sum(s))::int total_price , count(*) contract_count from (SELECT 
       (to_char(start_of_contract,'YYYY-MM-01'))::date as month_contract , price_contract s
  FROM public.contracts_contract where status = 'actual' ) q group by month_contract order by month_contract)qq;"""

    with  connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            data= row[0]
        else:
            data = {}
        return Response(row[0])


@api_view(['GET'])
def contract_accrual_data(request):
    sql = """select json_agg(row_to_json(res)) from (
select  qq.size_accrual,coalesce(q.sum_payment,0) as sum_payment, qq.date_accrual from (SELECT  sum(size_accrual) as size_accrual,date_accrual
  FROM public.contracts_registeraccrual group by date_accrual order by date_accrual)qq

  left join (SELECT to_char(payment_date,'YYYY-MM-01') as m_payment, sum(sum_payment) as sum_payment
  FROM public.contracts_registerpayment group by to_char(payment_date,'YYYY-MM-01'))q on q.m_payment::date = qq.date_accrual order by date_accrual
  )res;"""

    with  connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return Response(row[0])


@api_view(['GET'])
def contract_largest_debtors(request):
    sql = """select json_agg(row_to_json(qqq)) from (select full_name, s from (select contractor_id, sum(size_accrual) s from  (SELECT cc.contractor_id, size_accrual
  FROM public.contracts_registeraccrual  ca
  left join public.contracts_contract cc on cc.id = ca.contract_id )q group by contractor_id order by sum(size_accrual) desc limit 10)qq 
  left join public.l_core_coreorganization  ca on ca.id =  contractor_id order by s)qqq"""

    with  connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return Response(row[0])
