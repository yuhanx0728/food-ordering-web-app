# Food Ordering Web App

This is a final project for the course 17-437, Web Application Development in CMU.

The original idea comes from a [hackathon project](https://devpost.com/software/wai-mai-dpq4ou).

We improved on the originial idea and built a full-fledge Django web app for students to order food and arrange pickups at selected locations on campus. We also created a suite of analytics features for vendors, by integrating multiple chart APIs.
And most importantly, we tested and debugged the website for security loopholes, and deployed it on AWS as part of the project demo.

## How to bulk create dummy data

```
rm db.sqlite3
rm -rf takeout/migrations/0*
python3 manage.py makemigrations
python3 manage.py migrate
python3 create_data.py
python3 manage.py runserver
```

For usernames, check out data/User.csv(both vendors and customers).
Passwords for all users are just "password".
Redo the whole process every time you bulk create dummy data or it will show errors that multiple instances of the same objects are created.
