from django.db import models
from core.models import *

# Create your models here.
PAYMENT_METHOD = [
    ("cash", "Cash"),
    ("credit_card", "Credit Card"),
    ("debit_card", "Debit Card"),
    ("online", "Online Payment"),
]

class POS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pos")
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount percentage on total sale
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Tax percentage
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD,
        default="cash",
    )
    notes = models.TextField(blank=True, null=True)  # Additional notes about the sale

    @property
    def net_total(self):
        """Calculate the total after applying discount and adding tax."""
        discount_amount = (self.total_amount * self.discount) / 100
        taxable_amount = self.total_amount - discount_amount
        tax_amount = (taxable_amount * self.tax) / 100
        return taxable_amount + tax_amount

    def __str__(self):
        return f"POS Sale - {self.id} by {self.user.username}"

    class Meta:
        verbose_name = "POS Sale"
        verbose_name_plural = " POS Sales"


class POSItem(models.Model):
    pos = models.ForeignKey(POS, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount on item in percentage
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """Calculate the total price for the item after discount."""
        discount_amount = (self.sale_price * self.discount) / 100
        self.total_price = (self.sale_price - discount_amount) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for POS {self.pos.id}"

    class Meta:
        verbose_name = "POS Item"
        verbose_name_plural = "POS Items"