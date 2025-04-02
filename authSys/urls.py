
from django.urls import path, include
from . import views

urlpatterns = [
    path('register', views.register_member, name='register' ),
    path('login', views.login_member, name='login' ),
    path('logout', views.logout_member, name='logout' ),
]
