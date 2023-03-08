from django.urls import path
from . import views

urlpatterns = [
    path('edit-user-profile/<str:user_id>/', views.edit_user_profile, name='edit-user-profile'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('signup/', views.MySignUpView.as_view(), name='signup'),
    path('user-profile/', views.user_profile, name='user-profile'),
]
