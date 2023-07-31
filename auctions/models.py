from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    auctioneer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_item")
    name = models.CharField(max_length=64)
    description = models.TextField()
    url_image = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=64, null=True)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pk} => {self.name}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="auctions")
    bid = models.IntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidding", default=1)
    created_at = models.DateField(auto_now_add=True)
        
    def __str__(self):
        return f"Listing: {self.listing}, bid: {self.bid}, by: {self.bidder}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchers")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commenter")