from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from takeout.forms import *
from takeout.models import *
from takeout.charts import MealPieChart, SalesTrendChart, StackBarChart
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime #important if using timezones
from django.http import QueryDict
from django.core.exceptions import PermissionDenied
# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, Http404

# Used to send mail from within Django
from django.core.mail import send_mail

@login_required
def home_vendor(request):
    if not vendor_has_permission(request.user):
        raise PermissionDenied("You are not a vendor!")

    def total(meals):
        total_profit = 0
        total_vol = 0
        for meal in meals:
            total_profit += meal.price * meal.number_ordered
            total_vol += meal.number_ordered
        return total_profit, total_vol

    context = {}
    vendor_profile = VendorProfile.objects.get(vendor=request.user)
    # all vendor meals from today
    curr_day_vendor_meals = VendorMeal.objects.filter(vendor=vendor_profile,
                                                      date=timezone.now())
    # all vendor meals from the past week
    past_week_vendor_meals = VendorMeal.objects.filter(vendor=vendor_profile,
                                                       date__gte=timezone.now()-timezone.timedelta(days=7))

    # initialize all the charts
    meal_pie_cht = MealPieChart(meals=curr_day_vendor_meals)
    sales_trend_cht = SalesTrendChart(meals=past_week_vendor_meals)
    stk_bar_cht = StackBarChart(meals=curr_day_vendor_meals)

    # passing the charts into the context
    context['meal_pie_cht'] = meal_pie_cht.generate()
    context['sales_trend_cht'] = sales_trend_cht.generate()
    context['stk_bar_cht'] = stk_bar_cht.generate()

    # passing the meal objects and stats into the context
    context['meals'] = curr_day_vendor_meals
    context['totalProfit'], context['totalVolumes'] = total(curr_day_vendor_meals)
    context['vendor'] = vendor_profile
    return render(request, 'takeout/vendor_main.html', context)

@login_required
def home_customer(request):
    if not customer_has_permission(request.user):
        raise PermissionDenied("You are not a customer!")

    context = dict()
    context['vendors'] = VendorProfile.objects.all()
    context['meals'] = VendorMeal.objects.filter(date=timezone.now())
    return render(request, 'takeout/customer_main.html', context)

@login_required
def menu_detail(request, vendor_id):
    if not customer_has_permission(request.user):
        raise PermissionDenied("You are not a customer!")
    context = {}
    vendor_profile = VendorProfile.objects.get(vendor_id=vendor_id)
    context['vendor'] = vendor_profile
    context['meals'] = VendorMeal.objects.all().filter(
        vendor=vendor_profile, date=timezone.now())
    return render(request, 'takeout/menu_detail.html', context)

@login_required
def mealPic(request, id):
    meal =  get_object_or_404(VendorMeal, id=id)
    print(meal)
    print('Meal Picture #{} fetched from db'.format(id))
    if not meal.picture:
        raise Http404
    return HttpResponse(meal.picture, content_type=meal.content_type)

@login_required
def profilePic(request, id):
    user =  get_object_or_404(User, id=id)

    try:
        vendor = VendorProfile.objects.get(vendor=user)
        print(vendor)
        print('Vendor Profile Picture #{} fetched from db'.format(id))
        if not vendor.profile_pic:
            raise Http404
        return HttpResponse(vendor.profile_pic, content_type=vendor.content_type)

    except:
        customer = CustomerProfile.objects.get(customer=user)
        print(customer)
        print('Customer Profile Picture #{} fetched from db'.format(id))
        if not customer.profile_pic:
            raise Http404
        return HttpResponse(customer.profile_pic, content_type=customer.content_type)

@login_required
def add_to_cart(request, vendor_id, meal_id):
    if not customer_has_permission(request.user):
        raise PermissionDenied("You are not a customer!")
    vendor_profile = VendorProfile.objects.get(vendor_id=vendor_id)
    vendor_meal = VendorMeal.objects.get(pk=meal_id)
    if vendor_profile.vendor == request.user:
        return Http404

    customer_profile = CustomerProfile.objects.get(customer=request.user)
    try:
        order = Order.objects.get(customer_profile=customer_profile, paid=False)
        order.total_amount += (vendor_meal.price * int(request.POST['quantity']))
        order.save()
        try:
            curr_meal = CustomerMeal.objects.get(vendor_meal=vendor_meal, order=order)
            curr_meal.quantity += int(request.POST['quantity'])
            curr_meal.save()

        except CustomerMeal.DoesNotExist:
            new_meal = CustomerMeal(vendor_meal=vendor_meal, date=timezone.now(),
                                    order=order, quantity=request.POST['quantity'])
            new_meal.save()
    except Order.DoesNotExist:
        order = Order(customer_profile=customer_profile,
                      total_amount=(vendor_meal.price * int(request.POST['quantity'])),
                      status="Waiting for Payment")
        order.save()
        new_meal = CustomerMeal(vendor_meal=vendor_meal, date=timezone.now(),
                                order=order, quantity=request.POST['quantity'])
        new_meal.save()

    return redirect(menu_detail, vendor_id=vendor_id)

@login_required
def vendor_profile(request):
    if not vendor_has_permission(request.user):
        raise PermissionDenied("You are not a vendor!")
    profile_param = {
        'phone', 'time_slot', 'parking_location', 'car', 'profile_pic',
    }

    user_param = {
        'email',
    }

    if request.method == 'GET':
        curr_vendor = request.user
        curr_vendor_profile = curr_vendor.vendor_profile
        context = {
            'profile_form': VendorProfileForm({
                'phone': curr_vendor_profile.phone,
                'time_slot': curr_vendor_profile.time_slot,
                'parking_location': curr_vendor_profile.parking_location,
                'car': curr_vendor_profile.car
            }),
            'user_form': UserEditForm({
                'email': curr_vendor.email
            })
        }
        return render(request, 'takeout/vendor_profile.html', context)
    # POST request
    curr_vendor = request.user
    curr_vendor_profile = curr_vendor.vendor_profile

    if 'old-password' in request.POST and request.POST['old-password']:
        if not request.user.check_password(request.POST['old-password']):
            context = {
                'msg': 'Passwords do not match!',
                'profile_form': VendorProfileForm({
                    'phone': curr_vendor_profile.phone,
                    'time_slot': curr_vendor_profile.time_slot,
                    'parking_location': curr_vendor_profile.parking_location,
                    'car': curr_vendor_profile.car
                }),
                'user_form': UserEditForm({
                    'email': curr_vendor.email
                })
            }
            return render(request, 'takeout/vendor_profile.html', context)
        else:
            if 'new-password' not in request.POST or not request.POST['new-password']:
                context = {
                    'msg': 'Please enter new password!',
                    'profile_form': VendorProfileForm({
                        'phone': curr_vendor_profile.phone,
                        'time_slot': curr_vendor_profile.time_slot,
                        'parking_location': curr_vendor_profile.parking_location,
                        'car': curr_vendor_profile.car
                    }),
                    'user_form': UserEditForm({
                        'email': curr_vendor.email
                    })
                }
                return render(request, 'takeout/vendor_profile.html', context)
            curr_vendor.set_password(request.POST['new-password'])
            curr_vendor.save()

    d = {}
    for key in request.POST:
        if not request.POST[key]:
            if key in profile_param:
                d[key] = getattr(curr_vendor_profile, key)
            if key in user_param:
                d[key] = getattr(curr_vendor, key)
        else:
            d[key] = request.POST[key]

    qd = QueryDict('', mutable=True)
    qd.update(d)

    profile_form = VendorProfileForm(qd, request.FILES, instance=curr_vendor_profile)
    user_form = UserEditForm(qd, instance=curr_vendor)
    if profile_form.is_valid() and user_form.is_valid():
        profile_form.save()
        user_form.save()

        context = {
            'msg': 'Info Updated!',
            'profile_form': VendorProfileForm({
                'phone': curr_vendor_profile.phone,
                'time_slot': curr_vendor_profile.time_slot,
                'parking_location': curr_vendor_profile.parking_location,
                'car': curr_vendor_profile.car
            }),
            'user_form': UserEditForm({
                'email': curr_vendor.email
            })
        }
        return render(request, 'takeout/vendor_profile.html', context)
    # render empty forms regardless of whether
    context = {
        'profile_form': profile_form,
        'user_form': user_form
    }
    return render(request, 'takeout/vendor_profile.html', context)

@login_required
def shopping_cart(request):
    if not customer_has_permission(request.user):
        raise PermissionDenied("You are not a customer!")
    context = {}
    customer = CustomerProfile.objects.get(customer=request.user)

    try:
        curr_order = Order.objects.get(customer_profile=customer, paid=False)
    except:
        context = {'message_title': "No meal in the cart yet...",
                   'message_content': " What are you thinking of having today?",
                   'user': request.user}
        return render(request, 'takeout/message.html', context)

    if request.method == 'POST' and 'cancel' in request.POST:
        del_meal = CustomerMeal.objects.get(id=request.POST['cancel'])
        curr_order.total_amount -= del_meal.vendor_meal.price * del_meal.quantity
        del_meal.delete()

    cart_today = curr_order.customermeal_set.all().filter(date=timezone.now())

    try :
        meal = cart_today[0].vendor_meal

        context = {'meals': cart_today,
                   'key': meal.vendor.payment_key,
                   'user': request.user}
    except:
        context = {'message_title': "No meal in the cart yet...",
                   'message_content': " What are you thinking of having today?",
                   'user': request.user}
        return render(request, 'takeout/message.html', context)

    def total_charge(meals):
        sum = 0
        for meal in meals:
            sum += meal.vendor_meal.price * meal.quantity
        return sum
    context['totalCharge'] = total_charge(cart_today)

    return render(request, 'takeout/shopping_cart.html', context)

@login_required
def orders_history(request):
    if not customer_has_permission(request.user):
        raise PermissionDenied("You are not a customer!")
    context= {}
    customer_profile = CustomerProfile.objects.get(customer=request.user)
    orders = Order.objects.all().filter(customer_profile=customer_profile).exclude(paid=False)
    order_meals = []
    for order in orders:
        order_meals.append((order, CustomerMeal.objects.all().filter(
            order=order)))
    context['orders'] = order_meals
    context['user'] = request.user
    
    if orders.count() == 0:
        context = {'message_title': "Welcome to LotusPond!",
                   'message_content': " What are you thinking of having today?",
                   'user': request.user}
        return render(request, 'takeout/message.html', context)

    return render(request, 'takeout/customer_history.html', context)

@login_required
def charge(request):
    customer_profile = CustomerProfile.objects.get(customer=request.user)
    order = Order.objects.get(customer_profile=customer_profile, paid=False)
    meals = order.customermeal_set.all()
    for meal in meals:
        vendor_meal = meal.vendor_meal
        vendor_meal.number_ordered += meal.quantity
        vendor_meal.avail_quantity -= meal.quantity
        vendor_meal.save()
    order.paid = True
    order.status = "Ready for Pickup"
    order.save()
    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(request.user)

    email_body = """
    Your order was made successfully!
    Please click the link below to check your order details:

      http://{host}{path}
    """.format(host=request.get_host(),
               path=reverse('qrcode_page', kwargs={'order': order.id, 'token':token}))

    send_mail(subject="Order Success",
              message=email_body,
              from_email="webappteam36@gmail.com",
              recipient_list=[request.user.email])
    return render(request, 'takeout/order_success.html')

@login_required
def qrcode_page(request, order, token):
    context = {}
    #curr_order = Order.objects.get(id=order)
    #curr_user = curr_order.customer_profile.customer
    #if not default_token_generator.check_token(curr_user, token):
    #    raise Http404

    context['order'] = "http://3.19.30.158/takeout/pickup_confirmation/" + str(order)
    return render(request, 'takeout/qrcode_page.html', context)

@login_required
def order_success(request):
    return render(request, 'takeout/order_success.html')

@login_required
def customer_profile(request):
    if not customer_has_permission(request.user):
        raise PermissionDenied("You are not a customer!")
    profile_param = {
        'phone', 'profile_pic'
    }

    user_param = {
        'email', 'first_name', 'last_name'
    }

    if request.method == 'GET':
        curr_customer = request.user
        curr_customer_profile = request.user.customer_profile
        context = {
            'profile_form': CustomerProfileForm({
                'phone': curr_customer_profile.phone,
            }),
            'user_form': UserEditForm({
                'email': curr_customer.email,
                'first_name': curr_customer.first_name,
                'last_name': curr_customer.last_name,
            })
        }
        return render(request, 'takeout/customer_profile.html', context)
    # POST request
    curr_customer = request.user
    curr_customer_profile = curr_customer.customer_profile

    if 'old-password' in request.POST and request.POST['old-password']:
        if not request.user.check_password(request.POST['old-password']):
            context = {
                'msg': 'Passwords do not match!',
                'profile_form': CustomerProfileForm({
                    'phone': curr_customer_profile.phone,
                }),
                'user_form': UserEditForm({
                    'email': curr_customer.email,
                    'first_name': curr_customer.first_name,
                    'last_name': curr_customer.last_name,
                })
            }
            return render(request, 'takeout/customer_profile.html', context)
        else:
            if 'new-password' not in request.POST or not request.POST['new-password']:
                context = {
                    'msg': 'Please enter new password!',
                    'profile_form': CustomerProfileForm({
                        'phone': curr_customer_profile.phone,
                    }),
                    'user_form': UserEditForm({
                        'email': curr_customer.email,
                        'first_name': curr_customer.first_name,
                        'last_name': curr_customer.last_name,
                    })
                }
                return render(request, 'takeout/customer_profile.html', context)
            curr_customer.set_password(request.POST['new-password'])
            curr_customer.save()

    d = {}
    for key in request.POST:
        # if the value is empty then we use the old value in the models
        if not request.POST[key]:
            if key in profile_param:
                d[key] = getattr(curr_customer_profile, key)
            if key in user_param:
                d[key] = getattr(curr_customer, key)
        # if the value is not empty, we directly add it to the dict
        else:
            d[key] = request.POST[key]

    qd = QueryDict('', mutable=True)
    qd.update(d)

    profile_form = CustomerProfileForm(qd, request.FILES,
                                       instance=curr_customer_profile)
    user_form = UserEditForm(qd, instance=curr_customer)
    if profile_form.is_valid() and user_form.is_valid():
        profile_form.save()
        user_form.save()

        context = {
            'msg': 'Info Updated!',
            'profile_form': CustomerProfileForm({
                'phone': curr_customer_profile.phone,
            }),
            'user_form': UserEditForm({
                'email': curr_customer.email,
                'first_name': curr_customer.first_name,
                'last_name': curr_customer.last_name,
            })
        }
        return render(request, 'takeout/customer_profile.html', context)
    # render empty forms regardless of whether
    context = {
        'profile_form': profile_form,
        'user_form': user_form
    }
    return render(request, 'takeout/customer_profile.html', context)

@login_required
def pickup_confirmation(request, order):
    context = {}
    if request.method == 'GET':
        curr_order = Order.objects.get(id=order)
        if curr_order.status == "Picked up":
            return redirect(reverse('error_page'))
        context['order'] = curr_order
        meals = CustomerMeal.objects.all().filter(order=order)
        context['meals'] = meals
        return render(request, 'takeout/pickup_confirmation.html', context)
    curr_order = Order.objects.get(id=order)
    meals = CustomerMeal.objects.all().filter(order=curr_order)
    meal = meals[0]
    vendor = meal.vendor_meal.vendor.vendor
    if request.user != vendor:
        raise Http404
    curr_order.status = "Picked up"
    curr_order.save()
    return redirect(reverse('home_vendor'))

@login_required
def error_page(request):
    return render(request, 'takeout/error_page.html')

def customer_register_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = CustomerRegistrationForm()
        return render(request, 'takeout/register_customer.html', context)

    # POST request
    form = CustomerRegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'takeout/register_customer.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    # create the associated customer profile
    new_customer_profile = CustomerProfile(customer=new_user,
                                           andrew_id=form.cleaned_data['andrewID'],
                                           phone=form.cleaned_data['phone'])
    new_customer_profile.save()

    # login the new user
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)

    return redirect(reverse('home_customer'))

def vendor_register_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = VendorRegistrationForm()
        return render(request, 'takeout/register_vendor.html', context)

    # POST request
    form = VendorRegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'takeout/register_vendor.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'])
    new_user.save()

    new_vendor_profile = VendorProfile(vendor=new_user,
                                       phone=form.cleaned_data['phone'],
                                       company_name=form.cleaned_data['company_name'],
                                       license=form.cleaned_data['license'],
                                       payment_key=form.cleaned_data['payment_key'])

    new_vendor_profile.save()

    # login the vendor as a user
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    return redirect(reverse('home_vendor'))

def login_action(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['customer_form'] = CustomerLoginForm()
        context['vendor_form'] = VendorLoginForm()
        # default active tab is customer
        context['customer_tab_active'] = 'active'
        return render(request, 'takeout/login.html', context)

    if "customer-login" in request.POST:
        form = CustomerLoginForm(request.POST)
        context['customer_form'] = form
        # customer tab becomes active
        context['customer_tab_active'] = 'active'
        context['vendor_form'] = VendorLoginForm()
    else:
        form = VendorLoginForm(request.POST)
        context['vendor_form'] = form
        # vendor tab becomes active
        context['vendor_tab_active'] = 'active'
        context['customer_form'] = CustomerLoginForm()

    if not form.is_valid():
        print("not valid!")
        return render(request, 'takeout/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    if "customer-login" in request.POST:
        try:
            customer = CustomerProfile.objects.get(customer=new_user)
        except CustomerProfile.DoesNotExist:
            context['customer_error'] = 'This customer does not exist. Are ' \
                                        'you a ' \
                               'vendor instead?'
            return render(request, 'takeout/login.html', context)
    else:
        try:
            vendor = VendorProfile.objects.get(vendor=new_user)
        except VendorProfile.DoesNotExist:
            context['vendor_error'] = 'This vendor does not exist. Are you a ' \
                               'customer instead?'
            return render(request, 'takeout/login.html', context)

    login(request, new_user)

    if "customer-login" in request.POST:
        return redirect(reverse('home_customer'))
    return redirect(reverse('home_vendor'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

@login_required
def add_meal(request):
    if not vendor_has_permission(request.user):
        raise PermissionDenied("You are not a vendor!")
    context = {}
    curr_vendor = VendorProfile.objects.get(vendor=request.user)
    if request.method == 'GET':
        meals = reversed(VendorMeal.objects.all().filter(vendor=curr_vendor, date=timezone.now()))
        context = {'meals': meals, 'form': VendorMealForm(), 'vendor':curr_vendor}
        return render(request, 'takeout/vendor_menu.html', context)

    new_vendor_meal = VendorMeal(vendor=request.user.vendor_profile, date=timezone.now())
    new_meal_form = VendorMealForm(request.POST, request.FILES, instance=new_vendor_meal)

    if not new_meal_form.is_valid():
        context = {'form': new_meal_form, 'vendor':curr_vendor}
        return render(request, 'takeout/vendor_menu.html', context)

    pic = new_meal_form.cleaned_data['picture']
    print('Uploaded picture: {} (type={})'.format(pic, type(pic)))
    new_vendor_meal.content_type = pic.content_type
    new_meal_form.save()
    new_vendor_meal.save()
    curr_vendor = VendorProfile.objects.get(vendor=request.user)
    meals = reversed(VendorMeal.objects.filter(vendor=curr_vendor, date=timezone.now()))
    context = {'meals': meals, 'form': VendorMealForm, 'vendor':curr_vendor}
    return render(request, 'takeout/vendor_menu.html', context)

@login_required
def delete_meal(request, id):
    if not vendor_has_permission(request.user):
        raise PermissionDenied("You are not a vendor!")

    curr_vendor = VendorProfile.objects.get(vendor=request.user)
    meal = VendorMeal.objects.get(id=id)
    meal.delete()

    meals = reversed(VendorMeal.objects.all().filter(vendor=curr_vendor))
    context = {'meals': meals, 'form': VendorMealForm(), 'vendor':curr_vendor}
    return render(request, 'takeout/vendor_menu.html', context)

def customer_has_permission(user):
    try:
        customer = CustomerProfile.objects.get(customer=user)
        return True
    except CustomerProfile.DoesNotExist:
        return False

def vendor_has_permission(user):
    try:
        vendor = VendorProfile.objects.get(vendor=user)
        return True
    except VendorProfile.DoesNotExist:
        return False
