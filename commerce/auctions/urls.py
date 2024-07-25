from django.urls import path

from . import views

APP_NAME = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlist", views.createlist, name="createlist"),
    path("list_categories", views.list_categories, name="list_categories"),
    path("auctions/<int:listing_id>/listing_page", views.listing_page, name="listing_page"),
    path("watch_list", views.watch_list, name="watch_list"),
    path("auctions/<str:title>", views.cat_listings, name="cat_listings"),
    path("comments_page", views.comments_page, name="comments_page")
]
