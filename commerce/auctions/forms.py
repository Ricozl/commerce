from django import forms
from .models import Categories, Listing, Watchlist, Bid, Comment


class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['cat_name']
        cat_name = forms.ModelMultipleChoiceField(queryset=Categories.objects.all(), required=False, label="Category")


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'start_bid', 'image_url', 'is_active', 'creator', 'winner', 'listing_category']
        id = forms.IntegerField()
        title = forms.CharField(max_length=64)
        description = forms.CharField(max_length=512)
        start_bid = forms.DecimalField(max_digits=6, decimal_places=2)
        image_url = forms.URLField(max_length=1024, required=False)
        is_active = forms.BooleanField()
        creator = forms.IntegerField()
        winner = forms.CharField(max_length=64)
        listing_category = forms.ModelMultipleChoiceField(queryset=Categories.objects.all(), widget=forms.CheckboxSelectMultiple())
        widget = {
            'category': forms.CheckboxSelectMultiple,
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']
        widgets = {
            'bid': forms.NumberInput(attrs={'step':0.01, 'min':0.0})
            }


class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['item', 'watcher', 'is_active']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['item', 'name', 'commenter', 'text']


