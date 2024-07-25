from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Comment, Categories, Watchlist, Bid
from .forms import ListingForm, CommentForm, BidForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active="True")
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def createlist(request):
    # create new listing
    context = {}
    form = ListingForm(request.POST or None)
    context['form'] = form
    if request.method == "POST":
        # process submitted form for new listing
        if form.is_valid():
            # create new listing
            Listing.objects.create(**form.cleaned_data)
        else:
            # invalid form, return to Listing Form with error message
            messages.add_message(request, messages.WARNING,
                                "Problem with Listing. Try again.")
            return render(request, "auctions/createlisting.html", context)
        # return success message and take user to active listings page
        messages.add_message(request, messages.SUCCESS,
                            "New Listing was Saved.")
        return HttpResponseRedirect(reverse("index"))
    else:
        # send empty form (ListingForm) to be filled in by user
        return render(request, "auctions/createlisting.html", context)


def cat_listings(request, title):
    # get all active listings in this category
    active_list = Listing.objects.filter(
        listing_category__cat_name=title, is_active="True").values()
    # display all listings (as links) in this category
    return render(request, "auctions/cat_listings.html", {
        "title": title, "listings": active_list
    })


def listing_page(request, listing_id):
    # accumulate all data needed to display individual listing page
    # first get listing info for this listing_id
    try:
        lists = Listing.objects.get(id__exact=listing_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING,
                            "Listing doesn't exist.")
        return HttpResponseRedirect(reverse("index"))
    # get listing creator's id
    list_c = lists.creator

    # get creator's username from User model
    try:
        list_name = User.objects.get(id__exact=list_c)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.WARNING,
                            "Problem with User information.")
        return HttpResponseRedirect(reverse("index"))
    name = list_name.username

    # get category name for selected listing to display in listing_page
    cats = Categories.objects.filter(list_cat__exact=listing_id)
    for cat in cats:
        cat_list = cat.cat_name

    # get current price (highest bid) from Bid model
    high_bids = Bid.objects.filter(item__exact=listing_id).first()
    if not high_bids:
        # if no appropriate bids have been made, set price to starting price
        price = lists.start_bid
    else:
        # set price to highest bid
        price = high_bids.bid

    # POST method
    if request.method == "POST":
        # get signed-in user's id
        l_userid = request.user.id

        # get User instance for signed-in user
        try:
            u_w = User.objects.get(id__exact=l_userid)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING,
                                "User does not exist or is not signed in.")
            return HttpResponseRedirect(reverse('index'))
        # process various submit buttons from listing page
        if request.POST.get('save_watchlist'):
            # add listing to watchlist
            # check if listing already on watchlist, post warning message
            if Watchlist.objects.filter(watcher=u_w, item=listing_id, is_active=True).exists():
                messages.add_message(
                    request, messages.WARNING, "Listing is already on Watchlist")
            else:
                # if not already on watchlist, save to watchlist and send success message
                Watchlist.objects.create(
                    watcher=u_w, item=lists, is_active=True)
                messages.add_message(
                    request, messages.SUCCESS, "Listing is now on Watchlist")
            # display watchlist
            return HttpResponseRedirect(reverse('watch_list'))

        elif request.POST.get('remove_watchlist'):
            # remove item from watchlist, first check if on watchlist
            try:
                w_list = Watchlist.objects.get(
                    watcher=u_w, item=listing_id, is_active=True)
            except ObjectDoesNotExist:
                # send message that already on watchlist, display watchlist
                messages.add_message(
                    request, messages.WARNING, "Listing is not on Watchlist.")
                return HttpResponseRedirect(reverse('watch_list'))
            # if on watchlist, set active flag to "false" to remove from watchlist
            w_list.is_active = "False"
            # save updated field, is_active, to Watchlist
            w_list.save(update_fields=['is_active'])
            # post success message and display watchlist
            messages.add_message(request, messages.SUCCESS,
                                "Listing is removed from Watchist.")
            return HttpResponseRedirect(reverse('watch_list'))

        elif request.POST.get('add_comments'):
            # direct to new page with empty form for user to add comments
            context = {}
            form = CommentForm()
            context['form'] = form
            return render(request, "auctions/comments.html", {
                'form': context, 'listings': lists, 'listing_id': listing_id
            })

        elif request.POST.get('end_auction'):
            # process end of auction, first get winning bid from bid model
            win_bid = Bid.objects.filter(item__exact=listing_id).first()
            if win_bid:
                # if there is a bid saved, get winner's username
                b_name = win_bid.name
                # get user instance for winner
                try:
                    win_name = User.objects.get(username__exact=b_name)
                except ObjectDoesNotExist:
                    # if can't find user, return error message
                    messages.add_message(
                        request, messages.WARNING, "Can't find the Winner information.")
                    return HttpResponseRedirect(reverse('index'))
                # get winner's username
                winner = win_name.username
            else:
                # if no bid was recorded, set winner to none
                winner = "None"

            lists.winner = winner
            # set listing to inactive by setting active flag to "false"
            lists.is_active = "False"
            lists.save(update_fields=['is_active', 'winner'])

        elif request.POST.get('place_bid'):
            # get new bid from POST data
            new_bid = request.POST.get('bid')
            # compare new bid to current price
            if float(new_bid) > float(price):
                # if new bid is higher, save it to price variable
                new_price = ("{:0.2f}".format(float(new_bid)))
                price = new_price
                # create new bid instance in bid model, price, listing, user
                try:
                    Bid.objects.create(bid=price, item=lists, name=u_w)
                except IntegrityError:
                    messages.add_message(
                        request, messages.WARNING, "Error saving Bid. Please try again.")
                    return HttpResponseRedirect(reverse('index'))
                # save new current price in highest_bid field in Listing model
                lists.highest_bid = price
                lists.save(update_fields=['highest_bid'])
                # post success message on refreshed listing page
                messages.add_message(
                    request, messages.SUCCESS, "Your Bid is the New Current Price.")
            else:
                # post error message on refreshed listing page
                messages.add_message(
                    request, messages.WARNING, "Bid must be higher than Current Price.")

    # display detailed listing page for listing selected, including category name
    lists = Listing.objects.filter(id__exact=listing_id).values()
    # get all comments for this listing
    comms = Comment.objects.filter(item__exact=listing_id).values()
    # get empty form for bid
    context = {}
    form = BidForm()
    context['form'] = form
    # refresh listing page
    return render(request, "auctions/listing_page.html", {
        'listings': lists, 'l_cat': cat_list, 'listing_id': listing_id, 'comments': comms, 'creator': list_c, 'lister': name, 'form': form, 'price': price
    })


def list_categories(request):
    # displays all categories as links
    return render(request, 'auctions/categories_list.html', {
        'categories': Categories.objects.all()
    })


def watch_list(request):
    # get signed-in user's id
    wat_user = request.user.id
    # get all items on signed-in user's watchlist
    wat_lists = Watchlist.objects.filter(
        watcher=wat_user, is_active=True).select_related('item').order_by('item')
    # display user's watchlist
    return render(request, 'auctions/watch_list.html', {
        'watch_list': wat_lists
    })


def comments_page(request):
    # use CommentForm, either empty or with POST data
    form = CommentForm(request.POST or None)

    if request.method == "POST":
        # process submitted comments form
        # get signed-in user's username
        c_name = request.user.username
        if form.is_valid():
            # if form is valid, save and post success message
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                "Comments are saved to listing.")
        else:
            # if form is invalid, post error message
            messages.add_message(request, messages.WARNING,
                                "Comments couldn't be saved. Please try again.")
    return HttpResponseRedirect(reverse('index'))
