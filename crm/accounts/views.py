from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from django.contrib import messages
from .decorators import unathorized_user, allowed_user, admin_only
# Create your views here.

@unathorized_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Account Created Successfully.. for "+ username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)

@unathorized_user
def loginPage(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username or password is Incorrect!")

    context = {}
    return render(request, 'accounts/login.html', context)

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only(allowed_roles=['admin'])
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()
    context = {
        'orders': orders, 
        'customers': customers,
        'total_orders': total_orders,
        'delivered':delivered,
        'pending':pending
    }
    return render(request, 'accounts\home.html', context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts\products.html', {'products':products})


@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def user(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()
    context = {
        'orders': orders, 
        'total_orders': total_orders,
        'delivered':delivered,
        'pending':pending
    }
    return render(request, 'accounts\\user.html', context=context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def account_Settings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method =="POST":
        form = CustomerForm(request.POST, request.FILES,instance=customer)
        if form.is_valid():
            form.save()
            
    context = {'form': form}
    return render(request, 'accounts/account_settings.html', context=context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customers(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context= {
        'customer': customer, 
        'orders': orders,
        'total_orders': total_orders,
        'myFilter': myFilter
    }
    return render(request, 'accounts\customers.html', context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra = 10)
    customer = Customer.objects.get(id=pk)
    # form = OrderForm(initial = {'customer': customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset': formset}
    return render(request, 'accounts\order_create.html', context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def update_order(request, pk):
    order = Order.objects.get(id=pk)

    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts\order_create.html', context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect("/")

    context = {'item': order}
    return render(request, 'accounts\delete.html', context)