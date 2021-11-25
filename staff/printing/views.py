import base64

from django.http import JsonResponse
from django.shortcuts import render

TEST_DATA = """
Alexandria Library
The coolest place on the internet!!1!

Checkouts:
----------

Due: YESTERDAY!
The Trilogy: Book 4
  - Charles Dickens

Due: Tomorrow
The Trilogy: Book 5
  - Charles Dickens

Due: 2025/01/01
A Family's Guide to Silly Putty and Hair
  - Your Favorite Blogger

----------

You saved $4,000,000,405 by using your library!
"""


def generate_receipt(request):
    # todo: make this take in data + format it
    data = base64.urlsafe_b64encode(bytes(TEST_DATA, "utf-8")).decode()
    return JsonResponse({"data": data})


def index(request):
    return render(request, "staff/receipt_test_page.partial")
