
# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
stripe.api_key = "rk_test_51REzPYBUxEI2KOLvFD9b0XMfewiQXelHjds8bZ3k6p7dLJYq7B9EIakYL4tscIjfb2vDG7l2PC6jzxQUst53PMUy003d1o8Jn9"

location = stripe.terminal.Location.create(
  display_name="HQ",
  address={
    "line1": "1272 Valencia Street",
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "postal_code": "94110",
  },
  stripe_account="acct_1REzPYBUxEI2KOLv",
)














