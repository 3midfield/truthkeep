import random
import string

import stripe
from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import threading
import logging
from datetime import datetime, timedelta
import requests
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from rest_framework.response import Response
from rest_framework import status
import os
from sentiment.views.articles import get_and_parse_articles
from rest_framework.exceptions import APIException

import logging
logger = logging.getLogger("StandardLog")

class TransactionFailedException(APIException):
    '''
    custom exception used with stripe
    '''
    status_code = 400
    default_detail = "Transaction failed"
    default_code = "transaction_failed"

def create_customer(email, metadata):
    stripe.api_key =  os.getenv("STRIPE_SECRET_KEY", None) 

    try:
        customer = stripe.Customer.create(email=email, metadata=metadata)
        return customer
    except Exception as e:
        logger.error(
            "Stripe error during Create customer------------"
            + datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            + "-------"
            + str(e)
        )
        raise TransactionFailedException(
            {
                "statusCode": 400,
                "error": True,
                "message": "Something went wrong. Please try again later!",
                "data": {"message": "Something went wrong. Please try again later!"},
            }
        )