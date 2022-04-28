# Bespoke. Books. Battlestar Galactica.

![Automated Tests Status](https://github.com/AlexandriaILS/Alexandria/actions/workflows/tests.yml/badge.svg)

The plan here is to design and implement, mostly for the sake of practice, an integrated library system for a small library.

It should include:

* 🟠 open web view for patrons
* 🟠 searching by various fields
* 🟠 a locked-down web view for library staff
* 🟢 ability to add new titles
* 🟢 ability to import titles by MARC record
* 🟠 printing receipts
* 🟠 hold management
* 🔴 email notification capabilities
* 🔴 handle fines with Stripe
* 🟢 support for multiple locations
* 🟢 support for multiple systems
* 🔴 support for federated systems
* 🔴 support for books checked out by staff (no due date)
* 🔴 support for books that need to be weeded
* 🔴 support for replacing weeded books
* 🔴 investigate adding bookstore functionality for sale of weeded materials

...and probably more. ¯\\\_(ツ)_/¯

Read the docs here: https://alexandriails.github.io/Alexandria/

Getting started with developing: https://alexandriails.github.io/Alexandria/development/getting_started/

note for later: https://python-escpos.readthedocs.io/en/latest/index.html
