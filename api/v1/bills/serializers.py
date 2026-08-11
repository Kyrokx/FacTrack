from rest_framework import serializers
from bills.models import Bill

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            'id',
            'type',
            'period',
            'deadline',
            'price_total',
            'previous_index',
            'new_index',
            'total_consumption',
            'paid',
        ]