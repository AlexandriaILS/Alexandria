---
label: Welcome
icon: home
order: 1000
---
# AlexandriaILS

Alexandria is an Integrated Library System (ILS) that aims to be a free and open source replacement for the suffocatingly expensive software that many libraries are forced to take on. The goal of the project is to be able to perform all the day-to-day management duties that any small to medium-sized library might need while doing it as unobtrusively and quickly as possible. Built with longevity and maintainability in mind, Alexandria lets you put your library funds where they matter: serving your patrons.

> Without libraries what have we? We have no past and no future. _— Ray Bradbury_

## Features

Click on each of the below sections to get more details.

==- User-facing Catalog
The catalog is the heart and soul of any ILS - making sure that your patrons can access it and easily obtain the materials they need is critical. Patrons also have access to see their checkouts, limited account settings, due dates, holds, and fines & fees. (In case you're wondering, yes, you can disable fines for your library!)
===

==- Mobile (and Tablet!) Friendly
Desktops and laptops aren't the only devices that can access the internet, and so it's not much of a logical leap to say "let's make it all work on mobile"! The catalog, management, and business sides of the app are all mobile friendly, so you can do whatever you need to do on the go.
===

==- Catalog Management
Edit items, records, or holds as needed to keep your collection as clean as can be! Add new items of existing records or create new ones easily through our staff panel. Importing, modifying, and exporting MARC records is almost easier done than said - you can also import and export catalog information to the shared repository of all libraries using Alexandria for others to save a little work!
===

==- Patron Management
Create and edit patrons, handle fines and fees, and easily perform actions on their behalf to keep your library running smoothly. Per ALA guidelines, no checkout history is preserved after books are returned and the bare minimum of information is collected.
===

==- Reports
Generate whatever report you need, from financial data to daily pull lists to collection weeding, through our easy-to-use report tooling. Lockable to different permission levels, you can make sure that the right information is available to all staff at any time and that everyone has immediate access to the data they need.
===

==- Built-in Stripe Integration (or roll your own!)
Collecting fines or selling materials isn't always everyone's idea of fun, but we make it easy to get started by including a fully functional Stripe integration in the box - just put in the API keys and go! If you're a government entity or have a centralized payment system, you can easily hook into your payment system with a little bit of Python code and our extendable payment system.

This section also supports functionality that can be used for book sales or a small gift shop, allowing for easily keeping all the records under one data roof.
===

==- Federated Library Support
Not every library stands on its own; sometimes we band together for the good of all. Tie multiple instances of Alexandria together to share collections (or even just a collection or two) with other libraries.
===

==- Host it yourself (or don't!)
As part of the open source goal of the project, you are free to take this software and use it for your library! No fees, no charges, no nothing. Nada, zip, zilch.

If you can't (or don't want to, we wouldn't blame you) want to host it yourself, there is a cloud plan available that only requires a setup fee (to import your catalog, patrons, and other data) and a nominal monthly fee to keep everything going with backups.

!!!danger Hang on!
Open Source doesn't mean that you can host it and charge other people for access. The source code is open, but the license is as strict as we can make it while still allowing the folks who need it (libraries) to have open access. You are welcome to use it for your own library, but please contact us for hosting if you'd like someone else to handle the details.
!!!

===

## Why?

### No-to-Low Cost

Running a library is expensive, especially for small ones with only a handful of staff members. There are a lot of moving parts, and oftentimes each moving part comes with its own hefty price tag and a different vendor contract. The ILS (or in some cases, the many individual parts which may or may not work well together) is the heart of the library, but the very existence of a library is antithetical to making you pay out the nose for the software you functionally require. Free solutions often come with the cost of usability, and we don't want you to be stuck between blowing your budget on something pretty or a free option that's impossible to use.

We hope that Alexandria is the best of both worlds -- free, pretty, _and_ easy to use.

!!!success
There's no vendor lock-in here, and the only contracts are optional support or cloud hosting; otherwise, it's 100% free.
!!!

### A Simple Solution

"Simple" is almost a misnomer when talking about something this complicated, but what we mean is that we've worked with librarians and patrons to find the functionality that you need without extra bells and whistles that may look cool but, ultimately, are schlock.

That said, not every feature or default configuration works for every organization; we have lots of settings so that you can set up your library with exactly what you need without overwhelming staff or patrons. (And maybe there's something that you still need that we haven't addressed! If that's so, open an issue and let's work together to get that functionality implemented!) 

### Privacy First

There is no reason to collect more information about patrons than is strictly necessary, so... **we don't**.

Alexandria is built from the ground up using [ALA's Privacy Checklist for ILS'](https://www.ala.org/advocacy/privacy/checklists/library-management-systems) as a guide, and patron privacy is paramount. We store the absolute minimum that is required; no tracking, no history, no nothing. Data that doesn't exist can't be weaponized.

### Ease of Use

Alexandria is a web-based platform designed for easy navigation, access from anywhere, and usable by patrons and staff alike regardless of technological skill or knowledge. Our platform is built with accessibility in mind and follows the current [WCAG Accessibility guidelines](https://www.w3.org/TR/WCAG21/) and is natively usable with tooling like screen readers or custom fonts. Staff both behind the desk or in the stacks have access to the same tools using whatever device they have on hand, and mobile-friendly design means that what works on one device will work on another.

---

Alexandria straddles the middle ground between configurability and usability. A clean interface greets every user, giving patrons the information and access they need while giving librarians the power they need to keep the doors open.
