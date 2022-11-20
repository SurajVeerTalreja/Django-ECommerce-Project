from django.urls import reverse
from django.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)    # URL Path e.g. /shirts
    description = models.TextField(max_length=300, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


    def get_slug_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name