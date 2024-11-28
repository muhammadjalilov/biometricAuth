from django.urls import path

from authentication.views import (CustomLoginView, HomeView, logout_view,
                                  register)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("register/", register, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
]
