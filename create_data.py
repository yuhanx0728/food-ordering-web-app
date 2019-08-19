import csv, os

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps.settings'

import django
django.setup()

from takeout.models import *
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime, parse_date

def get_meal_pic(meal_name):
    if meal_name == "A":
        return 'meal1.jpg'
    elif meal_name == "B":
        return 'meal2.jpg'
    else:
        return 'meal3.jpg'

def get_profile_pic(user):
    if user == "1":
        return 'user1.jpg'
    elif user == "2":
        return 'user2.jpg'
    else:
        return 'user3.jpg'

with open('data/User.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        user = User.objects.create_user(
        	username=row[0],
            first_name=row[1],
            last_name=row[2],
            password=row[3],
            email=row[4]
            )
        user.save()
        print("User Created! username =", row[0])

with open('data/CustomerProfile.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = CustomerProfile.objects.get_or_create(
        	customer=User.objects.get(username=row[0]),
            andrew_id=row[1],
            phone=row[2],
            profile_pic=get_profile_pic(row[3])
            )
        if created:
	        print("Customer Profile Created! cutsomer =", row[0])

with open('data/VendorProfile.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = VendorProfile.objects.get_or_create(
        	vendor=User.objects.get(username=row[0]),
            phone=row[1],
            company_name=row[2],
            license=row[3],
            time_slot=row[4],
            parking_location=row[5],
            car=row[6],
            payment_key=row[7],
            profile_pic=get_profile_pic(row[8])
            )
        if created:
	        print("Vendor Profile Created! vendor =", row[0])

with open('data/VendorMeal.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        meal, created = VendorMeal.objects.get_or_create(
        	meal_detail=row[0],
            price=int(row[1]),
            vendor=VendorProfile.objects.get(vendor=User.objects.get(username=row[2])),
            number_ordered=int(row[3]),
            avail_quantity=int(row[4]),
            drink=row[5],
            meal_type=row[6],
            meal_name=row[7],
            date=row[8],
            picture=get_meal_pic(row[7])
            )
        meal.date = parse_date(row[8])
        meal.save()
        print("VENDOR MEAL: ", meal)
        if created:
	        print("Vendor Meal Created! vendor meal =", row[0], row[8])


# with open('data/CustomerMeal.csv') as f:
#     reader = csv.reader(f)
#     for row in reader:
#     	# 2012-02-21 10:28:45
#     	date = parse_datetime(row[2])
# 		pytz.timezone("US/Eastern").localize(date, is_dst=None)
#         _, created = CustomerMeal.objects.get_or_create(
# 			picked_up=bool(int(row[0])), 
# 			vendor_meal=VendorMeal.objects.get(id=row[1]), 
# 			date=date,
# 			order=Order.objects.get(id=row[3]),
# 			quantity=int(row[4])
#             )
#         if created:
# 	        print("Customer Meal Created! customer meal =", row[0])

# with open('data/Order.csv') as f:
#     reader = csv.reader(f)
#     for row in reader:
#     	if row[3] == '1':
#     		status = 'Waiting for checkout'
#     	else if row[3] == '2':
#     		status = 'Ready for pickup'
#     	else if row[3] == '3':
#     		status = 'Order Completed'
#     	else:
#     		status = 'Expired'
#         _, created = Order.objects.get_or_create(
#         	total_amount=int(row[0]), 
#         	customer_profile=CustomerProfile.objects.get(customer=User.objects.get(username=row[1])), 
#         	paid=bool(int(row[2])), 
#         	status=status
#             )
#         if created:
# 	        print("Order Created! order =", row[0])
