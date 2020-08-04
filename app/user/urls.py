from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    # ../user/create/
    # name='create' is used when calling the reverse() function
    # e.g. reverse('user:create')
    path('create/', views.CreateUserView.as_view(), name='create'),
    # ../user/token/
    path('token/', views.CreateTokenView.as_view(), name='token'),
    # ../user/token/
    path('me/', views.ManageUserView.as_view(), name='me'),
]
