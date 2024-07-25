from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Categories(models.Model):
    cat_name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ['cat_name']

    def __str__(self):
        return self.cat_name

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    start_bid = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=1024, blank=True)
    listing_category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="list_cat")
    is_active = models.BooleanField(default=False)
    creator = models.IntegerField()
    highest_bid = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    winner = models.CharField(max_length=64, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return "Listing title: {}, Starting Bid: {}, Listing Category: {}, Is_Active: {}, Creator: {}, Create Date: {}, Winner: {}, Highest Bid: {}, Description: {}, Image URL: {}".format(self.title, self.start_bid, self.listing_category.cat_name, self.is_active, self.creator, self.create_date, self.winner, self.highest_bid, self.description, self.image_url)


class Bid(models.Model):
    bid = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='b_item')
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='b_name')

    class Meta:
        ordering = ['-bid', 'item']

    def __str__(self):
        return "Bid: ${} on Listing: {} by {}".format(self.bid, self.item.title, self.name)

class Watchlist(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='w_list')
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='w_user')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['watcher', 'item']

    def __str__(self):
        return "Watcher: {}, Listing: {}, Is_active: {}".format(self.watcher, self.item.title, self.is_active)

class Comment(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='c_user')
    commenter = models.CharField(max_length=64, default='Anonymous')
    text = models.CharField(max_length=512, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['item', '-created_on']

    def __str__(self):
        return 'Listing: {}, Comment: {}, by {} on {}'.format(self.item.title, self.text, self.commenter, self.created_on)

