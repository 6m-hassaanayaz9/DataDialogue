from django.urls import path
from . import views 
from .views import LoginView
from .views import SignupView
from .views import LogoutView,get_database_names

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/',SignupView.as_view(), name='signup'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('get-database-names/',get_database_names, name='get_database_names')
]