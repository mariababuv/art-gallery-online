from email import message
from itertools import product
from turtle import home
from unicodedata import category
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from.models import Customer,Product,Cart,OrderPlaced
from.forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pandas as pd
from numpy import array 


class ProductView(View):
    def get(self,request):
        Men=Product.objects.filter(category='Men')
        Women=Product.objects.filter(category='Women')
        Child=Product.objects.filter(category='Child')
        return render(request,'app/home.html',{'Men':Men,'Women':Women,'Child':Child})


class ProductDetailView(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        print(product)

        product_name=product.title
        print("---------------------",product_name)
        recomendation=RecommendProduct(product_name)
        rec_array=[]
        for recomendations in recomendation:
            print("================",recomendations)
            recomends=Product.objects.get(title=recomendations)
            rec_array.append(recomends)
        print(rec_array)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'recomendations':rec_array})


def RecommendProduct(product_name):

    p_array=[]
    p_array.append(product_name)
    products_prob = pd.read_csv('C:/Users/Admin/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.10/footwearstore/products_prob.csv')
    basket = p_array
    print(basket)
    #Select the number of relevant items to suggest
    no_of_suggestions = 5

    all_of_basket = products_prob[basket]
    all_of_basket = all_of_basket.sort_values(by = basket, ascending=False)
    suggestions_to_customer = list(all_of_basket.index[:no_of_suggestions])

    # print('You may also consider buying:', suggestions_to_customer)

    recommend_array = []
    for recommendations in suggestions_to_customer:
        recommend_array.append(products_prob.loc[recommendations,'Unnamed: 0'])
    print(recommend_array) 
    return recommend_array     


@login_required
def add_to_cart(request):
    product_id= request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=request.user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0.0
        shipping_amount=50.0
        totalamount=0.0
        cart_product=[p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount=(p.quantity * p.product.discounted_price)
                amount+=tempamount
                totalamount=amount+shipping_amount
            return render(request,'app/addtocart.html',{'carts':cart,'totalamount':totalamount,'amount':amount})
        else:
            return render(request,'app/emptycart.html')

def plus_cart(request):
    if request.method=='GET':
        user=request.user
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity+=1
        c.save()
        amount=0.0
        shipping_amount=50.0
        cart_product=[p for p in Cart.objects.all() if p.user==user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount

        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount+shipping_amount,
            }
        return JsonResponse(data)

def minus_cart(request):
    if request.method=='GET':
        user=request.user
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity-=1
        c.save()
        amount=0.0
        shipping_amount=50.0
        cart_product=[p for p in Cart.objects.all() if p.user==user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount

        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount+shipping_amount,
            }
        return JsonResponse(data)

def remove_cart(request):
    if request.method=='GET':
        user=request.user
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.delete()
        amount=0.0
        shipping_amount=50.0
        cart_product=[p for p in Cart.objects.all() if p.user==user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount

        data={
            'amount':amount,
            'totalamount':amount+shipping_amount
            }
        return JsonResponse(data)


def buy_now(request):
 return render(request, 'app/buynow.html')

def profile(request):
 return render(request, 'app/profile.html')

@login_required
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})

@login_required
def orders(request):
 return render(request, 'app/orders.html')


def items(request,):
        items=Product.objects.filter(category='Men')
        return render(request, 'app/items.html',{'items':items})

def women(request,):
        women=Product.objects.filter(category='Women')
        return render(request, 'app/women.html',{'women':women})

def child(request,):
        child=Product.objects.filter(category='Child')
        return render(request, 'app/child.html',{'child':child})

class CustomerRegistrationView(View):
    def get(self,request):
        form= CustomerRegistrationForm()
        return render(request,'app/customerregistration.html',{'form':form})
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Successfully Registered')
            form.save()
        return render(request,'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):
    user=request.user
    add=Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=50.0
    totalamount=0.0
    cart_product=[p for p in Cart.objects.all() if p.user==user]
    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount
        totalamount=amount+shipping_amount
    return render(request, 'app/checkout.html',{'add':add,'totalamount':totalamount,'cart_items':cart_items})

@login_required
def payment_done(request):
    user=request.user
    custid=request.GET.get('custid')
    customers=Customer.objects.get(id=custid)
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, Customer=customers,product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form= CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})

    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            pincode=form.cleaned_data['pincode']
            landmark=form.cleaned_data['landmark']
            req=Customer(user=usr,name=name,locality=locality,city=city,pincode=pincode,landmark=landmark)
            req.save()
            messages.success(request,'Profile Updated')
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})
    
def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request,'app/orders.html',{'order_placed':op})


