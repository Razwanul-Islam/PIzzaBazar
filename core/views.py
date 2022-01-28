from operator import ge
from re import template
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
import environ
import stripe

from pizzaDelivary.settings import BASE_DIR
from .models import *


class HomePageView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()[:6]
        return context


class MenuPageView(ListView):
    model = Product
    template_name = 'menu.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('lower-price') and self.request.GET.get('upper-price'):
            context['products'] = Product.objects.filter(price__range=(
                self.request.GET.get('lower-price'), self.request.GET.get('upper-price')))
        elif self.request.GET.get('q'):
            context['products'] = Product.objects.filter(Q(name__icontains=self.request.GET.get(
                'q')) | Q(description__icontains=self.request.GET.get('q')))
        else:
            context['products'] = Product.objects.all()
        return context


class ProductView(DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(id=self.kwargs['pk'])
        context['sizes'] = context['product'].product_size_set.all()
        return context


class CartView(LoginRequiredMixin, ListView):
    login_url = '/account/login'
    model = CartItem
    template_name = 'cart.html'
    context_object_name = 'cartItems'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = CartItem.objects.filter(user=self.request.user)
        context['total_price'] = sum(
            product.subtotal_price for product in context['cart'])
        return context


class DeleteCartItem(LoginRequiredMixin, View):
    login_url = '/account/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        CartItem.objects.get(user=request.user, id=self.kwargs['pk']).delete()
        return redirect(reverse('cart'))


class AddToCart(LoginRequiredMixin, View):
    login_url = 'account/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        product_size = Product_size.objects.get(
            id=int(request.POST.get('size')))
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product_size)
        if created:
            cart_item.quantity = int(request.POST.get('quantity') or 1)
            cart_item.subtotal_price = cart_item.quantity * cart_item.product.price
            cart_item.save()
        else:
            cart_item.quantity = int(request.POST.get('quantity') or 1)
            cart_item.subtotal_price = cart_item.quantity * cart_item.product.price
            cart_item.save()
        return redirect(reverse('cart'))


class CheckoutView(LoginRequiredMixin, View):
    login_url = '/account/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        cart = CartItem.objects.filter(user=request.user)
        context = {
            'cart': cart,
            'total_price': sum(product.subtotal_price for product in cart)
        }
        return render(request, 'order.html', context)


class OrderView(LoginRequiredMixin, View):
    login_url = '/account/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        order = Order.objects.create(user=request.user, payment_method=request.POST.get('payment_method'), name=request.POST.get('name'), phone=request.POST.get('phone'), address=request.POST.get(
            'address'), email=request.POST.get('email') or request.user.email, order_note=request.POST.get('order_note'))
        if request.POST.get('lat'):
            order.lat=request.POST.get('lat')
            orderlng=request.POST.get('lng')

        cart = CartItem.objects.filter(user=request.user)
        sum = 0
        for item in cart:
            OrderItem.objects.create(order=order, product=item.product,
                                     quantity=item.quantity, subtotal_price=item.subtotal_price)
            sum += item.subtotal_price
            item.delete()
        order.total_price = sum
        if order.payment_method == 'cash':
            order.status = 'pending'
            order.save()
            return redirect(reverse('user_orders'))
        else:
            order.status = 'payment_pending'
            order.save()
            return redirect(reverse('create_checkout_session', args=[order.id]))


class UserOrdersView(LoginRequiredMixin, ListView):
    login_url = '/account/login'
    redirect_field_name = 'redirect_to'
    model = Order
    template_name = 'user-orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if(self.request.GET.get('status')):
            context['orders'] = Order.objects.filter(
                user=self.request.user, status=self.request.GET.get('status')).order_by("-created_at")
        else:
            context['orders'] = Order.objects.filter(user=self.request.user).order_by("-created_at")
        context['statuses'] = [('pending', 'Pending'),
                               ('payment_pending', 'Payment Pending'),
                               ('paid', 'Paid'),
                               ('shipping', 'Shipping'),
                               ('delivered', 'Delivered'),
                               ('cancelled', 'Cancelled'),
                               ('refunded', 'Refunded')]
        return context


# create check out session view
stripe.api_key = "sk_test_51H11ZJKQ7aeZAm3dgInJd3YK2MTVuOhr6MXptZJhb26CuZsKjDgGxQldPvnEoL1IQ5VJHZaEgXS3AWSjVr9ls3BF00sFzrUXVo"
YOUR_DOMAIN = 'http://127.0.0.1:8000'


class CreateCheckoutSessionView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['pk'])
        if order.payment_method == 'cash':
            order.status = 'pending'
            order.save()
            return redirect(reverse('user_orders'))
        if order.stripe_session_id:
            checkout_session = stripe.checkout.Session.retrieve(order.stripe_session_id)
        else:    
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        # 'price': i.product.stripe_price_id,
                        # 'quantity': i.quantity,
                        'name': i.product.product.name,
                        'amount': int(i.product.price*100),
                        'currency': 'usd',
                        'quantity': int(i.quantity),
                    } for i in order.orderitem_set.all()
                ],
                payment_method_types=['card'],
                mode='payment',
                success_url=YOUR_DOMAIN + '/payment/success/'+str(order.id),
                cancel_url=YOUR_DOMAIN + '/cancel',
            )
            
            order.stripe_session_id = checkout_session.id
            order.stripe_checkout_url = checkout_session.url
            order.save()
        
        return redirect(checkout_session.url, code=303)

class SuccessPaymentView(View):
    template = 'singleText.html'
    def get(self,request,**kwargs):
        id = kwargs.get("pk")
        order = get_object_or_404(Order,id = id)
        session = stripe.checkout.Session.retrieve(order.stripe_session_id)
        if session.payment_status == 'paid':
            order.status = 'paid'
            order.save()
            return render(request,self.template,{"text":"Your payment is successful . We will deliver your food as soon as possible."})

        else:
            return render(request,self.template,{"text":"Your payment is not completed"})

class CancelPaymentView(View):
    template = 'singleText.html'
    def get(self,request,**kwargs):
        return render(request,self.template,{"text":"You cancelled the payment"})
# Create your views here.
