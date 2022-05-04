import json
import os

from boto3 import Session as AWSSession
from requests_aws4auth import AWS4Auth

from gql import gql
from gql.client import Client
from gql.transport.requests import RequestsHTTPTransport


def make_client():
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    aws = AWSSession(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION_NAME'))
    credentials = aws.get_credentials().get_frozen_credentials()

    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        aws.region_name,
        'appsync',
        session_token=credentials.token,
    )

    transport = RequestsHTTPTransport(url=os.getenv('APPSYNC_ENDPOINT'),
                                      headers=headers,
                                      auth=auth)
    client = Client(transport=transport,
                    fetch_schema_from_transport=True)
    return client

# getMatch and update_appsync_obj are GraphQL queries in string form.
# You can make one using AppSync's query sandbox and copy the text over.

from .queries import getMatch
def test_get():
    # get_appsync_obj is a GraphQL query in string form.
    # You can use the query strings from AppSync schema.
    client = make_client()
    params = {'id': 2,'title': "test"}
    resp = client.execute(gql(getMatch),
                          variable_values=json.dumps(params))
    return resp


# def test_mutation():
#     client = make_client()
#     params = {'id': 1235, 'state': 'DONE!'}
#     resp = client.execute(gql(updateMatch),
#                           variable_values=json.dumps({'input': params}))
#     return resp