"""
This should be everything you need to build a cheap self-check-out station.
Ideally this should only require a raspberry pi and a scanner, this should
have the following functionality:

* single page (primarily, login doesn't count)
* requires staff login to start (don't want people checking out arbitrary materials at home)
* offers print ability for receipts
* offers email receipt
"""
from django.shortcuts import render


def index(request):
    return render(request, "selfcheckout/selfcheck_start.html")
