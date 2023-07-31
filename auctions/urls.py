from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.show, name="show"),
    path("categories", views.categories, name="categories"),
    path("bid", views.bid, name="bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>/close", views.close_bid, name="close_bid"),
    path("listing/<int:listing_id>/comment" , views.comment, name="comment")
]
