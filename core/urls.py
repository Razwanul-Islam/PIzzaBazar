from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('',HomePageView.as_view(),name="home"),
    path('product/<int:pk>',ProductView.as_view(),name="product"),
    path('add-to-cart',AddToCart.as_view(),name="add_to_cart"),
    path('cart',CartView.as_view(),name='cart'),
    path('cart/delete/<int:pk>',DeleteCartItem.as_view(),name="delete_cart_item"),
    path('menu',MenuPageView.as_view(),name="menu"),
    path('checkout',CheckoutView.as_view(),name="checkout"),
    path('order',OrderView.as_view(),name="order"),
    path('my-orders',UserOrdersView.as_view(),name="user_orders"),
    # Checkout Session
    path('checkout/create/<int:pk>',CreateCheckoutSessionView.as_view(),name="create_checkout_session"),
    path('payment/success/<int:pk>',SuccessPaymentView.as_view(),name="success_payment"),
    path('payment/canc',SuccessPaymentView.as_view(),name="cancel_payment")

]