# Customizations

The following keys are used in `default.json` and additional configs if used for a cloud deployment.

Base library information:

```json
{
  "name": "Neverland Library",
  "url": "https://alexandrialibrary.dev",
  "logo_url": null,
  "address": null,
  "phone_number": null
}
```

The following are used for the default keys in address fields when signing up a user -- change these to match the area
that this is deployed in.

```json
{
  "default_address_state_or_region": "IN",
  "default_address_city": "Indianapolis",
  "default_address_zip_code": "46227",
  "default_address_country": "USA"
}
```

Allow keeping track of how much patrons have saved by using the library; this is a privacy-centric value that only
tallies the total value of the books on their account as a single integer.

```json
{
  "enable_running_borrow_saved_money": true
}
```

Enable this if no material has a home branch location.

```json
{
  "floating_collection": false
}
```

Certain words get stripped out of searches so that they don't muck up the results. Adjust those values here:

```json
{
  "ignored_search_terms": [
    "a",
    "an",
    "the"
  ]
}
```

When adding new materials, the home location will default to a single place until it can be edited. Usually this is the
first place that's added when the system is first configured, but if it's not then just set the ID of the target
location here. For example, if the ID of a processing center is #3, then you'd set a 3 here.

```json
{
  "default_location_id": 1
}
```

The base URL and configuration settings for Zenodotus, the head librarian service for Alexandria. It keeps copies of
base Records to speed up importing and to serve as a backup. Downloading is always available, and uploading is
optional (but recommended) -- it helps out other users of Alexandria!

```json
{
  "zenodotus_url": "https://zenodotus.alexandrialibrary.dev/api/",
  "zenodotus_auto_upload": true
}
```

How many times can an object be renewed? How long should we set the default checkout duration? (That can be changed per
item type, fyi.)

```json
{
  "default_max_renews": 5,
  "default_checkout_duration_days": 21
}
```
