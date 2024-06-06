from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path('profile/<int:user_id>',views.profile, name='profile'),
    path('authorization/<int:user_id>', views.authorization, name='authorization'),
    path('', views.test, name='test'),
]