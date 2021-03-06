# django-fluo-coupons

A reuseable Django application for coupon gereration and handling
This is a customized fork of https://github.com/byteweaver/django-coupons.git


## Setup instructions

1. Install `django-fluo-coupons` via pip:
   ```
   $ python3 -m pip install django-fluo-coupons
   -
   ```

2. Add `'coupons'` to `INSTALLED_APPS` in `settings.py`.

3. Migrate database:

   ```
   $ python3 manage.py migrate
   ```

## Supported use cases of coupons

This application supports different kind of coupons in the way how they can be redeemed.
The difference is defined by the number of possible redeems and if they are bound to a specific user (may even be a list of users) or not.

    1) single time (default), coupon can be used one time without being bound to an user.
    2) user limited, coupon can be used one time but only by a specific user.
    3) limit number, coupon can be used a limited number of times, by any user once.
    4) users list, coupon can be used by a defined list of users, each once.
    5) unlimited, coupon can be used unlimited times, but only once by the same user.

## Contributors
(alphabetical order)

* @akuryou
* @ikresoft
* @marshallds
* @noxan
* @TigerDX
* @TimFletcher

## Changelog

### V 1.2.0a13

 * renamed Coupon.UserLimitError to Coupon.IsUsableError
 * removed redeem_done signal (use COUPONS_REDEEM_PIPELINE)

### V 1.2.0a12

 * added COUPONS_IS_USABLE_PIPELINE support
 * added COUPONS_REDEEM_PIPELINE support
 * drop python < 3 support
 * drop django < 1.10 support

### V 1.2.0

* Drop support for Django < 1.8
* Drop pyhon2 support
* Can save generate codes in csv file

### V 1.1.0
 * campaigns
   Coupons may now be associated with campaigns for better tracking
 * segmented coupon codes
   Coupon codes may now be segmented like "xxxx-xxxx-xx"
   New settings (defaults):
    * COUPONS_SEGMENTED_CODES (False)
    * COUPONS_SEGMENT_LENGTH (4)
    * COUPONS_SEGMENT_SEPARATOR ("-")
 * prefixes for coupon codes
   Coupons may now be auto prefixed upon creation
 * expiration date for coupons
   Coupons can now expire, see valid_until field
 * migrations for south and django 1.7+ included
 * django 1.8 now officially supported
 * minor fixes

### V 1.0.4
redeem_done signal

### V 1.0.3
Typo and CouponForm fix.

### V 1.0.2
Fixed Typo in settings.
* COUPNS_CODE_LENGTH -> COUPONS_CODE_LENGTH
* COUPNS_CODE_CHARS -> COUPONS_CODE_CHARS

*Check your settings after updating!*

### V 1.0.1
add django 1.7 migrations and south legacy migrations

### V 1.0.0
Supports:
* django 1.4 - 1.7
* python 2.7, 3.4
