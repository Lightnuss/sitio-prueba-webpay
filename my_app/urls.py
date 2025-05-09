from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_form, name='payment_form'),
    path('create/', views.create_payment, name='create_payment'),
    path('response/', views.payment_response, name='payment_response'),
]