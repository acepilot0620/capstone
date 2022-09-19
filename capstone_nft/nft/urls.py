from django.urls import include, path
from .views import (
    my_token,
)

urlpatterns = [
    path('my_token/', my_token, name='my_token'),
]