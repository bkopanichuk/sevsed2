from django.conf.urls import url, include
from .views import UAOauthLoginView


urlpatterns = [
    url(r'uaoauth/', UAOauthLoginView.as_view()),

]
