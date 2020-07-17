from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    customer = models.OneToOneField(User,
                                    default=None, on_delete=models.PROTECT,
                                    related_name='customer_profile')
    andrew_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=12)
    profile_pic = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, default='image/jpg')

    def __str__(self):
        return 'Customer Profile for: ' + self.customer.first_name + ' ' + \
               self.customer.last_name + ' , andrew ID is: ' + self.andrew_id

class VendorProfile(models.Model):
    vendor = models.OneToOneField(User, default=None, on_delete=models.PROTECT,
                                  related_name='vendor_profile')
    phone = models.CharField(max_length=12)
    company_name = models.CharField(max_length=20)
    license = models.CharField(max_length=100)
    time_slot = models.CharField(max_length=200)
    parking_location = models.CharField(max_length=200)
    car = models.CharField(max_length=200)
    profile_pic = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, default='image/jpg')
    payment_key = models.CharField(max_length=50)

    def __str__(self):
        return 'Vendor Profile for: ' + self.company_name

class Order(models.Model):
    total_amount = models.IntegerField()
    customer_profile = models.ForeignKey(CustomerProfile,
                                         default=None, on_delete=models.PROTECT)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20)

    def __str__(self):
        return 'Order amount is: ' + str(self.total_amount) + \
               ' , for customer: ' + self.customer_profile.customer.first_name + ' ' + self.customer_profile.customer.last_name + \
               ' , status is: ' + self.status


class VendorMeal(models.Model):
    meal_detail = models.CharField(max_length=200)
    price = models.IntegerField()
    vendor = models.ForeignKey(VendorProfile,
                               default=None, on_delete=models.PROTECT)
    number_ordered = models.IntegerField(default=0)
    avail_quantity = models.IntegerField()
    drink = models.CharField(max_length=50)
    meal_type = models.CharField(max_length=20)
    meal_name = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True, editable=True)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, default='image/jpg')
    
    def __str__(self):
        return 'Vendor meal detail is: ' + self.meal_detail + \
               ' , price is: ' + str(self.price) + \
               ' , vendor is: ' + self.vendor.company_name + \
               ' , number ordered is: ' + str(self.number_ordered) + \
               ' , drink is: ' + self.drink + \
               ' , date is: ' + str(self.date)

class CustomerMeal(models.Model):
    picked_up = models.BooleanField(default=False)
    vendor_meal = models.ForeignKey(VendorMeal,
                                    # when a VendorMeal is deleted, all
                                    # associated CustomerMeals are deleted on
                                    # cascade
                                    default=None, on_delete=models.CASCADE)
    date = models.DateField()
    order = models.ForeignKey(Order, default=None, on_delete=models.PROTECT)
    quantity=models.IntegerField(default=0)

    def __str__(self):
        return 'Customer meal status is: ' + str(self.picked_up) + \
               ' , meal type is: ' + str(self.vendor_meal) + \
               ' , date is: ' + str(self.date) + \
               ' , order is: ' + str(self.order)
