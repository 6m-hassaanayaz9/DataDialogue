from django.urls import path
from . import views 
from .views import LoginView
from .views import SignupView
from .views import LogoutView,QueryView,ConversationsView,LoadPreviousView,CreateConversation,SaveMessage,GetDatabaseNames,AccessPrivateDatabase
from .views import validateToken

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/',SignupView.as_view(), name='signup'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('get-database-names/',GetDatabaseNames.as_view(), name='get_database_names'),
    path('get-query-result/',QueryView.as_view(), name='get-query-result'),
    path('get-conversations/',ConversationsView.as_view(), name='get_conversations'),
    path('load-previous-messages/',LoadPreviousView.as_view(), name='load_previous'),
    path('create-conversation/',CreateConversation.as_view(), name='create-conversation'),
    path('save-message/',SaveMessage.as_view(), name='save-message'),
    path('validateToken/',validateToken.as_view(), name='validateToken'),
    path('access-private-database/',AccessPrivateDatabase.as_view(), name='access-private-database')
    
    
]