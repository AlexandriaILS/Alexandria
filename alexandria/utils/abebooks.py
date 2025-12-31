"""
(The MIT License)

Copyright (c) 2020 Ricardo Avila

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Retrieved from https://github.com/ravila4/abebooks on 2021/11/28

Modifications by @itsthejoker.
"""

import requests


class AbeBooks:
    def _get_price(self, payload):
        url = "https://www.abebooks.com/servlet/DWRestService/pricingservice"
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        return resp.json()

    def _get_recommendations(self, payload):
        url = "https://www.abebooks.com/servlet/RecommendationsApi"
        resp = requests.get(url, params=payload)
        resp.raise_for_status()
        return resp.json()

    def get_price_by_isbn(self, isbn):
        """
        Parameters
        ----------
        isbn (int) - a book's ISBN code
        """
        payload = {
            "action": "getPricingDataByISBN",
            "isbn": isbn,
            "container": "pricingService-{}".format(isbn),
        }
        return self._get_price(payload)

    def get_price_by_author_title(self, author, title):
        """
        Parameters
        ----------
        author (str) - book author
        title (str) - book title
        """
        payload = {
            "action": "getPricingDataForAuthorTitleStandardAddToBasket",
            "an": author,
            "tn": title,
            "container": "oe-search-all",
        }
        return self._get_price(payload)

    def get_price_by_author_title_binding(self, author, title, binding):
        """
        Parameters
        ----------
        author (str) - book author
        title (str) - book title
        binding(str) - one of 'hard', or 'soft'
        """
        if binding == "hard":
            container = "priced-from-hard"
        elif binding == "soft":
            container = "priced-from-soft"
        else:
            raise ValueError('Invalid parameter. Binding must be "hard" or "soft"')
        payload = {
            "action": "getPricingDataForAuthorTitleBindingRefinements",
            "an": author,
            "tn": title,
            "container": container,
        }
        return self._get_price(payload)

    def get_recommendations_by_isbn(self, isbn):
        """
        Parameters
        ----------
        isbn (int) - a book's ISBN code
        """
        payload = {"pageId": "plp", "itemIsbn13": isbn}
        return self._get_recommendations(payload)
