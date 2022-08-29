from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import View, TemplateView, CreateView, FormView
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
from .forms import *

class SearchView(TemplateView):
    template_name = "search.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        order = Orders.objects.get(confirmed=False)
        items = order.items_set.all()
        results = Product.objects.filter(
            Q(name__icontains=kw) | Q(description__icontains=kw) | Q(slug__icontains=kw))
        print(results)
        context = {
            "results": results,
            'items':items,
            'order':order
        }
        return context

def HomeView(request):
    template_name = "home.html"
    products = Product.objects.all()
    category = Category.objects.all()
    order, created = Orders.objects.get_or_create(confirmed=False)
    item = Items.objects.filter(order=order)
    items = order.items_set.all()
    if request.method == "POST":
        order.delete()
        return redirect("home")
    context = {
        'products':products,
        'category':category,
        'order':order,
        'item':item,
        'items':items
    }
    return render(request, template_name, context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    productprice = (float(data['form']['productprice']))
    product = Product.objects.get(id=productId)
    order = Orders.objects.get(confirmed = False)
    orderItem , created = Items.objects.get_or_create(order=order, product=product, price=productprice)

    if action =='add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action =='remove':
        orderItem.quantity = (orderItem.quantity -1)
    elif action =='delete':
        orderItem.quantity = 0
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    print('Action:', action)
    print('productId:', productId)
    return JsonResponse('Item is added to the table order', safe=False)

@login_required
def Dashboard(request):
    if request.user.is_staff:
        template_name = "dashboard/dashboard.html"
        product = Product.objects.all()
        category = Category.objects.all()
        context = {
            'product':product,
            'category':category
        }
        return render(request, template_name, context)
    else:
        return redirect('login')

@login_required
def CategoryDetail(request, pk):
    template_name = "dashboard/categorydetail.html"
    category = Category.objects.filter(id=pk)
    context = {
        'category':category
    }
    return render(request, template_name, context)

@login_required
def EditProduct(request, pk):
    template_name = "dashboard/editproduct.html"
    product = Product.objects.get(id=pk)
    form = ProductForm(instance = product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
        return redirect("reception-home")
    context = {
        'product':product,
        'form':form
    }
    return render(request, template_name, context)

@login_required
def AddProduct(request):
    template_name = "dashboard/addproduct.html"
    category = Category.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('allproducts')
    else:
        form = ProductForm()
    context = {
        'category':category,
        'form':form
    }
    return render(request, template_name, context)
@login_required
def AddCategory(request):
    template_name = "dashboard/addcategory.html"
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('allproducts')
    context = {
        'form':form
    }
    return render(request, template_name, context)

@login_required
def EditCategory(request, pk):
    template_name = "dashboard/editcategory.html"
    category = Category.objects.get(id=pk)
    form = CategoryForm(instance = category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
        return redirect("allproducts")
    context = {
        'category':category,
        'form':form
    }
    return render(request, template_name, context)

    

class RegistrationView(CreateView):
    template_name = "register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("login")
    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Sorry! Receptionist with this username already exists. please try new email.")
        if User.objects.filter(email=email).exists():
            return HttpResponse("Sorry! Receptionist with this email already exists. please try new email.")
        user = User.objects.create_user(username, email, password, is_staff=True)
        form.instance.user = user
        return super().form_valid(form)
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url
        

