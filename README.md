# Project description

We built a Django web app to sell/order food and arrange pickups between students and food vendors.

This is a final project for the course 17-437, Web Application Development in CMU, even though the original idea comes from my [hackathon project](https://devpost.com/software/wai-mai-dpq4ou).

# Tech stack
Django, PostgreSQL, Materialize CSS, AWS EC2

# How to run the web app locally
Clone this repository and do the following:
```
rm db.sqlite3
rm -rf takeout/migrations/0*
python3 manage.py makemigrations
python3 manage.py migrate
python3 create_data.py // bulk create dummy data
python3 manage.py runserver
```
Refer to `data/User.csv` to log in as either a vendor or a customer.
