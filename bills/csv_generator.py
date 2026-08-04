# dans bills/utils.py
import csv
from django.http import HttpResponse
import datetime

def generate_bills_csv(bills):
    export_date = datetime.date.today().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="factrack_factures_{export_date}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Type', 'Periode', 'Date limite', 'Prix total (FCFA)', 'Ancien index', 'Nouvel index', 'Consommation', 'Statut'])

    for bill in bills:
        writer.writerow([
            bill.id,
            bill.type,
            bill.period.strftime('%m/%Y') if bill.period else '',
            bill.deadline.strftime('%d/%m/%Y') if bill.deadline else '',
            bill.price_total,
            bill.previous_index,
            bill.new_index,
            bill.total_consumption,
            'Payée' if bill.paid else 'Impayée',
        ])

    return response