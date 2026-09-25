"""URL configuration for the blog application."""

from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.list__posts, name="post-list"),
    path("create/", views.create__post, name="create_post"),
    path("create/success/", views.success_page__post, name="success_page"),
    path("<str:date>/<str:cat>/<int:pk>/", views.detail__post, name="post-detail"),
    path("<int:pk>/comment/", views.add_comment, name="add-comment"),
    path("comment/<int:pk>/deactivate/", views.deactivate_comment, name="deactivate-comment"),
    path("comment/<int:pk>/edit/", views.edit_comment, name="edit-comment"),
]