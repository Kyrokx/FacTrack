from django.db import models


class Bill(models.Model):
    TYPE_CHOICES = [
        ('SONABEL', 'Electricity'),
        ('ONEA', 'Water'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    period = models.DateField()
    deadline = models.DateField()
    price_total = models.DecimalField(max_digits=10, decimal_places=2)
    previous_index = models.IntegerField()
    new_index = models.IntegerField()
    total_consumption = models.IntegerField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} - {self.period.strftime('%m-%Y')}"

    class Meta:
        ordering = ['-period']