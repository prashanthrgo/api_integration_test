from datetime import datetime

import jsonschema
import requests
import json
from jsonschema import validate
from pytest_schema import schema
import pandas as pd
from pandas import DataFrame

# Describe what kind of json you expect.
krakenschema = {
        "$schema": "https://json-schema.org/schema#",

        "type": "object",

        "error": {"type": "number"},
        "result": {
            "type": "number",
            "properties": {
                "unixtime": {"type": "number"},
                "rfc1123": {"type": "number"},

                "required": ["unixtime", "rfc1123"]
            }
        }
    }


def test_check_status_code_equals200():
    # Validate Response
    response = requests.get('https://api.kraken.com/0/public/Time')
    assert response.status_code == 200
    print(response.json())


def test_schema():
    # Validate Schema
    url = 'https://api.kraken.com/0/public/Time'

    # Additional headers.
    headers = {'Content-Type': 'application/json'}

    # Body
    schema = {
        "$schema": "https://json-schema.org/schema#",

        "type": "object",

        "error": {"type": "array"},
        "result": {
            "type": "object",
            "properties": {
                "unixtime": {"type": "integer"},
                "rfc1123": {"type": "string"},

                "required": ["unixtime", "rfc1123"]
            }
        }
    }

    # convert dict to json by json.dumps() for body data.
    response = requests.get(url)
    # json_data = json.loads(response.data)

    # Validate response headers and body contents, e.g. status code.
    # Validate response content type header
    assert response.headers["Content-Type"] == "application/json; charset=utf-8"

    resp_body = response.json()

    # Validate will raise exception if given json is not
    # what is described in schema.
    validate(instance=resp_body, schema=schema)


def test_price():
    # check if the top ask price is greater than top bid price
    url = 'https://api.kraken.com/0/public/Depth?pair=XBTUSD'
    response = requests.get(url)
    resp_body = response.json()
    askprice = resp_body['result']['XXBTZUSD']['asks'][0][0]
    bidprice = resp_body['result']['XXBTZUSD']['bids'][0][0]
    assert askprice >= bidprice
    print(askprice + ">" + bidprice)


def test_topofbook():
    url = 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD'
    response = requests.get(url)
    resp_body = response.json()
    tbkprice = resp_body['result']['XXBTZUSD']['a'][0]
    sndprice = resp_body['result']['XXBTZUSD']['b'][0]
    assert tbkprice > sndprice
    print("top of the book price for XXBTZUSD = " + tbkprice)


def test_checktimestaamp():
    url = 'https://api.kraken.com/0/public/OHLC?pair=XBTUSD'
    response = requests.get(url)
    resp_body = response.json()
    df = DataFrame(resp_body['result']['XXBTZUSD'][0])
    # df = pd.Series(resp_body, index=['time', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8'], dtype='object')
    df.columns = [0]
    # convert dates
    df.date = pd.to_datetime(df[0], unit='s')
    time1 = df.date[0].strftime("%H:%M:%S.%f - %b %d %Y")
    ds = DataFrame(resp_body['result']['XXBTZUSD'][1])
    ds.columns[0]
    ds.date = pd.to_datetime(ds[0], unit='s')
    time2 = ds.date[0].strftime("%H:%M:%S.%f - %b %d %Y")
    assert df.date[0] < ds.date[0]
    print(time1 + " < " + time2)


def test_check_InvalidAPI():
    # Validate Response
    response = requests.get('https://api.kraken.com/0/public/')
    assert response.status_code == 404
    print(response.json())


def test_datatypeSchema():
    # Validate Schema
    url = 'https://api.kraken.com/0/public/Time'

    # Additional headers.
    headers = {'Content-Type': 'application/json'}



    # convert dict to json by json.dumps() for body data.
    response = requests.get(url)
    teststr2=json.dumps(response.json())
    jsonData = json.loads(teststr2)

    # validate it
    isValid = valjson(jsonData)
    if isValid:
        print(teststr2)
        print("Given JSON data is Valid")
    else:
        print(teststr2)
        print("Given JSON data is InValid")




def valjson(jsonData):
    try:
        validate(instance=jsonData, schema=krakenschema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True
