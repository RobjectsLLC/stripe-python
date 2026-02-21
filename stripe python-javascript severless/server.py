#! /usr/bin/env python3.10

# Python 3.10 or newer required.

import json
import os
import stripe

# This is your test secret API key.
stripe.api_key = 'rk_test_51REzPYBUxEI2KOLvFD9b0XMfewiQXelHjds8bZ3k6p7dLJYq7B9EIakYL4tscIjfb2vDG7l2PC6jzxQUst53PMUy003d1o8Jn9'

from flask import Flask, jsonify, request, render_template


app = Flask(__name__, static_folder='public',
            static_url_path='', template_folder='public')

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/create_location', methods=['POST'])
def create_location():
  data = json.loads(request.data)

  location = stripe.terminal.Location.create(
    display_name=data['display_name'],
    address={
      'line1': data['address']['line1'],
      'city': data['address']['city'],
      'state': data['address']['state'],
      'country': data['address']['country'],
      'postal_code': data['address']['postal_code'],
    },
  )

  return location

@app.route('/register_reader', methods=['POST'])
def register_reader():
  data = json.loads(request.data)

  reader = stripe.terminal.Reader.create(
    location=data['location_id'],
    label='Quickstart - S700 Simulated Reader',
    registration_code='simulated-s700'
  )

  return reader

@app.route('/create_payment_intent', methods=['POST'])
def secret():
  data = json.loads(request.data)

  # For Terminal payments, the 'payment_method_types' parameter must include
  # 'card_present'.
  # To automatically capture funds when a charge is authorized,
  # set `capture_method` to `automatic`.
  intent = stripe.PaymentIntent.create(
    amount=data['amount'],
    currency='usd',
    payment_method_types=[
      'card_present',
    ],
    capture_method='automatic',
    payment_method_options={
      "card_present": {
        "capture_method": "manual_preferred"
      }
    }
  )
  return intent

@app.route('/process_payment', methods=['POST'])
def process_payment():
  data = json.loads(request.data)

  tries = 3
  for attempt in range(tries):
    try:
      reader = stripe.terminal.Reader.process_payment_intent(
        data['reader_id'],
        payment_intent=data['payment_intent_id'],
      )
      return reader
    except stripe.error.InvalidRequestError as e:
      if e.code == 'terminal_reader_timeout':
        # Temporary networking blip, automatically retry a few times.
        if attempt < tries - 1:
          continue
        else:
          return e.json_body
      elif e.code == 'terminal_reader_offline':
        # Reader is offline and won't respond to API requests. Make sure the reader is powered on
        # and connected to the internet before retrying.
        app.logger.error(e)
        return e.json_body
      elif e.code == 'terminal_reader_busy':
        # Reader is currently busy processing another request, installing updates or changing settings.
        # Remember to disable the pay button in your point-of-sale application while waiting for a
        # reader to respond to an API request.
        app.logger.error(e)
        return e.json_body
      elif e.code == 'intent_invalid_state':
        # Check PaymentIntent status because it's not ready to be processed. It might have been already
        # successfully processed or canceled.
        payment_intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
        app.logger.error('PaymentIntent is already in %s state.' % payment_intent.status)
        return e.json_body
      else:
        app.logger.error(e)
        return e.json_body

@app.route('/simulate_payment', methods=['POST'])
def simulate_payment():
  data = json.loads(request.data)

  options = {
      "card_present": {
          "number": data['card_number']
      },
      "type": "card_present"
  }

  reader = stripe.terminal.Reader.TestHelpers.present_payment_method(
    data['reader_id'],
    **options
  )

  return reader


@app.route('/capture_payment_intent', methods=['POST'])
def capture():
  data = json.loads(request.data)

  intent = stripe.PaymentIntent.capture(
    data['payment_intent_id']
  )

  return intent

if __name__ == '__main__':
    app.run()