from django.urls import path
from . import views

urlpatterns = [
    path("profile", views.profile, name="profile"),
    path("set_name", views.set_name, name="set_name"),
    path("revoke_authorization", views.revoke_authorization,
         name="revoke_authorization"),
    path("guest_sign_in", views.guest_sign_in, name="guest_sign_in"),
    path("redirect_action", views.redirect_action, name="redirect_action"),
    path("return_from_authorization", views.return_from_authorization,
         name="return_from_authorization"),
    path("", views.index, name="index"),
]
