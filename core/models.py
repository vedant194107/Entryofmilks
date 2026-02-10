from django.db import models

class Price(models.Model):
    price_per_liter = models.FloatField()

    def __str__(self):
        return f"₹ {self.price_per_liter}"


class Entry(models.Model):
    MILK_CHOICES = [
        ('cow', 'Cow'),
        ('buffalo', 'Buffalo'),
    ]

    milk_type = models.CharField(
        max_length=10,
        choices=MILK_CHOICES
    )
    liter = models.FloatField()
    price_per_liter = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.milk_type} - {self.liter}L - ₹{self.amount}"

