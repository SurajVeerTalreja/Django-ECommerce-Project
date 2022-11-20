from django.db import models
from store.models import Product, Variation
from accounts.models import Account

# Imagine this Database as two things:
# i) We need "Cart" to shop
# ii) We will keep "Products" inside the cart that we picked
# Hence we will be interested in specific cart (the one we picked for shopping) & products only inside it.

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank=True)  # Will be the session key of browser
    date_added = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return (self.product.price) * (self.quantity)

    def __unicode__(self) -> str:   # return unicode while returning an object (not string)
        return self.product