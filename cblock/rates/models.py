from django.db import models

from cblock.consts import MAX_AMOUNT_LEN


class UsdRate(models.Model):
    rate = models.DecimalField(max_digits=MAX_AMOUNT_LEN, decimal_places=2, blank=True, null=True, default=None)
    symbol = models.CharField(max_length=20, blank=True, null=True, default=None)
    name = models.CharField(max_length=100, blank=True, null=True, default=None)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.symbol

