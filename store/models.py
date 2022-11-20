from django.urls import reverse
from django.db import models
from category.models import Category

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=600, blank=True)
    price = models.FloatField()
    product_images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE) # CASCADE will delete the product once category is deleted
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    def get_product_detail(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True).order_by('id')
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True).order_by('id')

variation_category_choices = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    # Since we're returning complete object, __str__ will give an error
    # Because __str__ expects strings to be returned and not complete OBJECT
    def __str__(self):
        return f"{self.product.product_name} with {self.variation_category} {self.variation_value}"