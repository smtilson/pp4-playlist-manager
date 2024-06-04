from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path('', views.test, name='test'),
]