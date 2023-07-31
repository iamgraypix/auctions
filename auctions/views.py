from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max

from .models import User, Listing, Bid, Watchlist, Comment


class ListingForm(forms.Form):
    name = forms.CharField(max_length=64)
    bid = forms.IntegerField()
    description = forms.CharField()


class BidForm(forms.Form):
    new_bid = forms.IntegerField()

class CommentForm(forms.Form):
    comment = forms.CharField()

def login_required(f):
    def wrap(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated:
            return f(*args, **kwargs)

        return HttpResponseRedirect(reverse('login'))

    return wrap

def is_watchlisted(user, listing):
    watchlist = Watchlist.objects.filter(user=user)
    for row in watchlist:
        if listing == row.listing:
            return True
    return False


def index(request):

    # Get the distinct names from the Listing model
    # Check also if request has categories
    listings = Listing.objects.filter(is_active=True) if not bool(
        request.GET) else Listing.objects.filter(is_active=True, category=request.GET['category'])

    # List to store the final distinct rows
    auctions = []
    # print(listings)
    # Iterate over the distinct names
    for listing in listings:

        # Get the rows with the highest bid for each name
        rows = Bid.objects.filter(
            listing=listing).order_by('-bid')[:1]

        # Add the row to the final_rows list
        auctions.extend(rows)
    print(auctions)
    return render(request, "auctions/index.html", {
        "auctions": auctions
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
                "message": "Invalid username and/or password.",
                'type': "alert-danger"
            })
    else:
        return render(request, "auctions/login.html")


@login_required
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


@login_required
def create(request):

    if request.method == "POST":

        listing_form = ListingForm(request.POST)
        if listing_form.is_valid():
            name = listing_form.cleaned_data['name']
            description = listing_form.cleaned_data['description']
            bid = listing_form.cleaned_data['bid']
            url_image = request.POST['url_image']
            category = request.POST['category']

            # Saved the listing details
            listing = Listing(auctioneer=request.user, name=name, description=description,
                              url_image=url_image, category=category)
            listing.save()

            Bid(listing=listing, bid=bid).save()

            print(listing.pk)

        else:
            return render(request, "auctions/create.html", {
                'name_errors': listing_form.errors.get('name'),
                'bid_errors': listing_form.errors.get('bid'),
                'description_errors': listing_form.errors.get('description')
            })

        return HttpResponseRedirect(reverse('show', args=(listing.pk,)) + '?e=-1')

    return render(request, "auctions/create.html")


def show(request, listing_id):

    e = request.GET['e'] if bool(request.GET) else None
    # Check if it has some error in listing page
    if e == '0':
        message = ['Success! Your bid is the current bid', 'alert-success']
    elif e == '-1':
        message = ['New Listing Added Successfully', 'alert-success']
    elif e == '-2':
        message = ['New Comment Added!', 'alert-success']
    elif e == '1':
        message = ['Bid field is required and must be a number', 'alert-danger']
    elif e == '2':
        message = ['Invalid! Your entry bid is less or equal to current bid', 'alert-danger']
    elif e == '3':
        message = ['Unauthorized Access!', 'alert-danger']
    elif e == '4':
        message = ['Sorry this listing is no longer active', 'alert-danger']
    elif e == '5':
        message = ['Commend field is required!', 'alert-danger']
    else:
        message = ['', '']
        

    listing = Listing.objects.get(pk=listing_id)
    on_watchlist = False
    logged_in = request.user.is_authenticated

    comments = Comment.objects.filter(listing=listing)

    if logged_in:
        on_watchlist = is_watchlisted(request.user, listing=listing)

    
    if request.method == "POST":
        if logged_in:
            if on_watchlist:
                w = Watchlist.objects.get(listing=listing, user=request.user)
                w.delete()
                on_watchlist = False
            else:
                Watchlist(user=request.user, listing=listing).save()
                on_watchlist = True
            
        else:
            return HttpResponseRedirect(reverse('login'))


    return render(request, "auctions/show.html", {
        "auction": listing.auctions.order_by('-bid').first(),
        "bid_counter": len(Bid.objects.filter(listing=listing_id)),
        "on_watchlist": on_watchlist,
        "message": message[0],
        'type': message[1],
        'comments': comments
    })


@login_required
def bid(request):
    if request.method == "POST":
        
        bid = BidForm(request.POST)
        listing_id = request.POST['listing_id']

        # Get the highest bid 
        auction = Listing.objects.get(
            pk=listing_id).auctions.order_by('-bid').first()

        # Ensure listing is active
        if not auction.listing.is_active:
            return HttpResponseRedirect(reverse('show', args=(auction.listing.id,)) + '?e=4')


        if bid.is_valid():
            new_bid = int(bid.cleaned_data['new_bid'])
            listing = auction.listing
            current_bid = auction.bid

            if new_bid <= current_bid:
                # Report an error in listing page
                return HttpResponseRedirect( reverse('show', args=(listing_id,)) + '?e=2')

            Bid(listing=listing, bid=new_bid, bidder=request.user).save()

            # Report a message in listing page

            return HttpResponseRedirect(reverse('show', args=(listing_id,)) + '?e=0')
        
        # Report an error in listing page
        return HttpResponseRedirect(reverse('show', args=(listing_id)) + '?e=1')



def categories(request):

    categories = Listing.objects.values(
        'category').distinct().order_by('category').filter(is_active=True)

    print(categories)

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


@login_required
def watchlist(request):
    query = Watchlist.objects.filter(user=request.user)
    watchlist = []
    for row in query:
        listing = Bid.objects.filter(listing=row.listing).order_by('-bid')[:1]
        
        watchlist.extend(listing)


    print(watchlist)

    return render(request, "auctions/watchlist.html", {
        'watchlist': watchlist
    })


@login_required
def close_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # Ensure the auctioneer is the user
    if request.user != listing.auctioneer:
        return HttpResponseRedirect(reverse('show', args=(listing_id,)) + '?e=3')
    
    listing.is_active = False
    listing.save()

    return HttpResponseRedirect(reverse('show', args=(listing_id,)))


@login_required
def comment(request, listing_id):

    commentForm = CommentForm(request.POST)

    if commentForm.is_valid():
        
        user = request.user
        comment = commentForm.cleaned_data['comment']
        listing = Listing.objects.get(pk=listing_id)
        
        Comment(user=user, comment=comment, listing=listing).save()

        return HttpResponseRedirect(reverse('show', args=(listing_id,)) + '?e=-2')

    else:
        return HttpResponseRedirect(reverse('show', args=(listing_id,)) + '?e=5')