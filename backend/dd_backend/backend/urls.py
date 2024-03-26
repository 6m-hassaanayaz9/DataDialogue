from django.urls import path
from . import views 
from .views import LoginView
from .views import SignupView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/',SignupView.as_view(), name='signup'),
]