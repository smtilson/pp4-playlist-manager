from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("create_queue", views.create_queue, name="create_queue"),
    path("edit_queue/<int:queue_id>", views.edit_queue, name="edit_queue"),
    path("add_entry/<int:queue_id>/<str:video_id>", views.add_entry, name="add_entry"),
    path(
        "delete_entry/<int:queue_id>/<str:entry_id>",
        views.delete_entry,
        name="delete_entry",
    ),
    path("sync/<int:queue_id>", views.sync, name="sync"),
    path("gain_access/<str:queue_secret>/<str:owner_secret>", views.gain_access,name="gain_access"),
    path(
        "delete_queue/<int:queue_id>",
        views.delete_queue,
        name="delete_queue",
    ),
    path("earlier/<int:queue_id>/<int:entry_id>",views.earlier,name="earlier"),
    path("later/<int:queue_id>/<int:entry_id>",views.later,name="later"),
    path("swap/<int:queue_id>/<int:entry_id>",views.swap,name="swap"),
    path("swap-js/<int:queue_id>/<int:entry_id>/<int:other_entry_position>",views.swap_js,name="swap_js"),
    path("publish/<int:queue_id>", views.publish, name="publish"),
]
