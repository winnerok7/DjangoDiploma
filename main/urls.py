from django.urls import path
from .views import *

app_name = 'main'
urlpatterns=[
    path('accounts/login/', UserLogin.as_view(), name='login'),
    path('accounts/logout/', UserLogOut.as_view(), name='logout'),
    path('accounts/profile/change/<int:pk>/', profile_ad_change, name='profile_ad_change'),
    path('accounts/profile/delete/<int:pk>/',profile_ad_delete,name = 'profile_ad_delete'),
    path('accounts/profile/add/',profile_ad_add,name='profile_ad_add'),
    path('accounts/profile/<int:pk>/', profile_ad_page, name='profile_ad_page'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/info/',UserInfo.as_view(), name='change_info'),
    path('accounts/change_pass',ChangePassword.as_view(),name='change_password'),
    path('accounts/register/',RegisterUser.as_view(),name='register'),
    path('accounts/register/done/',RegisterFinal.as_view(),name='register_final'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='reg_activate'),
    path('accounts/profile/delete/',DeleteUser.as_view(),name='delete_user'),
    path('<int:heading_pk>/<int:pk>/',detail, name = 'detail'),
    path('<int:pk>/',by_heading,name='by_heading'),
    path('<str:page>/', other_page, name='other'),
    path('contacts/',contacts, name='contacts'),
    path('about/', about, name='about'),
    path('accounts/index/',index,name= 'index'),
    path('', main, name = 'main'),
]

