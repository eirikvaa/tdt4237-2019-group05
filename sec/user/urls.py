from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/security_question/<str:email>/', views.SecurityQuestionView.as_view(), name='sec_question'),
    path('signup/user_email', views.UserEmailView.as_view(), name='user_email'),
    path('signup/new_password', views.ConfirmTemporaryPasswordAndCreateNewPassword.as_view(), name='conf_new_password'),
    path('', include('django.contrib.auth.urls')),
    path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.activate,
         name='activate'),
]
