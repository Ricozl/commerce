from django.contrib import admin
from auctions.models import Listing, Categories, Bid, Comment, Watchlist


# Register your models here.

admin.site.register(Listing)
admin.site.register(Categories)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)