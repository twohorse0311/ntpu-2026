from django.urls import path

from .views import HomeView, TextResponseView, JsonResponseView, GoHomeView, GreetingView

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("text-response/", TextResponseView.as_view(), name="text-response"),
    path("json/", JsonResponseView.as_view(), name="json"),
    path("123123123/", GoHomeView.as_view(), name="go-home"),
    path("greeting/", GreetingView.as_view(), name="greeting"),

]
