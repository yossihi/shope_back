from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    desc = models.CharField(max_length=50, null=False, default="default description", unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    createdTime = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(null=True,blank=True,default='/placeholder.png')
    def __str__(self):
        return self.desc
    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    createdTime = models.DateTimeField(default=datetime.now, blank=True)
    total = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    def __str__(self) -> str:
        return f"{self.customer.username}, {self.id}"
    
class Order_Detail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    def __str__(self) -> str:
        return f"customer: {self.order_id.customer.username}, order number {self.order_id.id}, product: {self.product_id.desc}"