from datetime import datetime
import json

def ask_for_price(hotel_date):
    # hotel_date = 03-08-2019
    day_of_Month = hotel_date.split('-')
    days = day_of_Month[1]
    month_numb = int(day_of_Month[0])

    hotel_date = datetime.strptime(hotel_date, '%m-%d-%Y')

    if days[-1] == '1':
        days += 'st'
    elif days[-1] == '2':
        days += 'nd'
    elif days[-1] == '3':
        days += 'rd'
    else:
        days += 'th'


    message = "Hey, I'm looking for a hotel room on the " + days + " of " + hotel_date.strftime('%B') + ". What are you guys charging per night?"
    return message


def negotiate1(raw_json, cheap_hotel, cheapest_price):
    # First Haggle Attempt
    raw_json = json.loads(raw_json)

    
    pos = str(cheapest_price).find('.')
    if pos > -1:
        cheapest_price = cheapest_price[:pos]

    original_price = raw_json['entities'][0]['resolution']['value']
    original_price = original_price.replace('$', '')
    pos = str(original_price).find('.')
    if pos > -1:
        original_price =  str(original_price[:pos])
    current_price = str(int(original_price) * 0.8)
    pos = current_price.find('.')
    if pos > -1:
        current_price = int(current_price[:pos]) 
    current_price -= int(current_price)%5
    message = "Well, " + cheap_hotel + " down the road is charging " + cheapest_price + " dollars, can you do something like " + str(current_price) + " dollars?"
    status = 1
    intent = raw_json['topScoringIntent']['intent']

    if intent == 'No':
        message, status = final_no()
    return message, int(original_price), int(current_price), status

def negotiate2(raw_json, customer_name, current_price, original_price):
    # Second Attempt to haggle
    raw_json = json.loads(raw_json)
    intent = raw_json['topScoringIntent']['intent']
    
    if intent == 'Yes':
        message, status = agreement(customer_name)
        status = 2
        return message, current_price, status
    else:
        sentiment =raw_json['sentimentAnalysis']['score']
        status = 1
        if sentiment > 0.5:
            message = "Hmm.. well that is the highest I can go."
        else:
            message = "Alright.. Well, I'm I was really looking forward to staying there, can you meet me half way?"
            current_price = str((int(original_price) + int(current_price))/2)
            current_price = current_price[:current_price.find('.')]

        return message, current_price, status


def final_attempt(raw_json, customer_name):
    # This is it, just a yes or a no!
    raw_json = json.loads(raw_json)
    intent = raw_json['topScoringIntent']['intent']
    if intent == 'Yes':
        message, status = agreement(customer_name)
    else:
        message, status = final_no()
    return message, status


def final_no():
    # Update database
    # End Call
    # Start next call
    message = "Thanks anyways. Have a good day"
    status = -1
    return message, status


def agreement(customer_name):
    message = "Perfect. I'll book it under " + customer_name
    status = 2
    return message, status


def booked():
    # Update database
    # End calls
    message = "Thank you. Have a nice day!"
    status = 3
    return message, status
