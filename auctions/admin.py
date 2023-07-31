from django.contrib import admin

from .models import Listing, User, Bid, Watchlist, Comment

# Register your models here.


class ListingAdmin(admin.ModelAdmin):
    list_display = ("auctioneer", "id", "name", "description",
                    "url_image", "category", "is_active")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "bid", "bidder")


class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "listing")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "listing")


admin.site.register(Listing, ListingAdmin)
admin.site.register(User)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Comment, CommentAdmin)
