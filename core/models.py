from django.db import models

# Create your models here.

class Price(models.Model):
    price_per_liter = models.FloatField()

    def __str__(self):
        return f"₹{self.price_per_liter}"


class Entry(models.Model):
    liter = models.FloatField()
    price_per_liter = models.FloatField()
    amount = models.FloatField()
    # date = models.DateField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.liter} L - ₹{self.amount}"