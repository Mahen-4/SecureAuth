
from django.urls import path, include
from . import views

urlpatterns = [
    path('register', views.register_member, name='register' ),
    path('login', views.login_member, name='login' ),
    path('logout', views.logout_member, name='logout' ),
    path('code_a2f', views.code_a2f_member, name="code_a2f"),
    path('reset_password', views.reset_password_member, name="reset_password"),
    path('new_password/<uuid:uuid>', views.new_password_member, name="new_password"),
]
