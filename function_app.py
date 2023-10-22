import azure.functions as func
from azure.data.tables import TableClient
import logging
import json
from datetime import datetime

import os
from flask import Flask, Response,  request , jsonify

flask_app = Flask(__name__) 

conn_string = os.environ["AzureWebJobsStorage"]

app = func.WsgiFunctionApp(app=flask_app.wsgi_app, 
                           http_auth_level=func.AuthLevel.ANONYMOUS)

@flask_app.route('/gifts', methods=['GET'])
def get_gifts():
    logging.info('Python HTTP trigger function processed a request. GET ALL')
    table_client = TableClient.from_connection_string(conn_str=conn_string, table_name="gifts")
    my_filter = "PartitionKey eq 'gift'"
    all_gifts = table_client.query_entities(my_filter)
    logging.info('Query read')

    records = []

    for entity in all_gifts:
        records.append(entity)
    logging.info('records appended')
    return jsonify(records)

@flask_app.route('/gifts/<int:row_id>', methods=['GET'])
def get_gift(row_id):
    logging.info(f'Python HTTP trigger function processed a request. GET One with id {row_id}')
    table_client = TableClient.from_connection_string(conn_str=conn_string, table_name="gifts")
    my_filter = "PartitionKey eq 'gift' and RowKey eq '" + str(row_id) + "'"
    db_result = table_client.query_entities(my_filter)

    for item in db_result:
        logging.info(item)
        return jsonify(item)

    return {"error": "gift not found"}, 404



@flask_app.route('/gifts', methods=['POST'])
def create_gift():
    logging.info('Python HTTP trigger function processed a request. POST new gift')
    new_gift = request.get_json()
    new_gift["PartitionKey"] = "gift"
    new_gift["RowKey"] = str(new_gift["id"])
    new_gift["bought"] = False
    new_gift["gifted"] = False

    table_client = TableClient.from_connection_string(conn_str=conn_string, table_name="gifts")
    table_client.create_entity(new_gift)
    logging.info("record added")

    return jsonify(new_gift), 201


@flask_app.route('/gifts/<int:gift_id>', methods=['PUT'])
def update_gift_by_id(gift_id):
    
    logging.info(f'Update gift with id {gift_id}')
    table_client = TableClient.from_connection_string(conn_str=conn_string, table_name="gifts")

    try:
        gift = table_client.get_entity(partition_key='gift', row_key=str(gift_id))
    except:
        return {"error": "gift not found"}, 404

    body = request.get_json()
    if 'name' in body:
        gift['name'] = body['name']
    if 'cost' in body:
        gift['cost'] = body['cost']
    if 'bought' in body:
        gift['bought'] = body['bought']
    if 'gifted' in body:
        gift['gifted'] = body['gifted']
    if 'gift' in body:
        gift['gift'] = body['gift']
    if 'url' in body:
        gift['url'] = body['url']
    if 'occasion' in body:
        gift['occasion'] = body['occasion']
    
    table_client.update_entity(mode='merge', entity=gift)
    return jsonify(gift)



@flask_app.route('/gifts/<int:gift_id>', methods=['DELETE'])
def delete_gift_by_id(gift_id):
    logging.info(f'Delete gift with id {gift_id}')
    table_client = TableClient.from_connection_string(conn_str=conn_string, table_name="gifts")
    filter = f"PartitionKey eq 'gift' and RowKey eq '{str(gift_id)}'"

    db_result = table_client.query_entities(filter)

    for item in db_result:
        table_client.delete_entity(row_key=str(gift_id), partition_key="gift")
        return jsonify({'result': True})

    return {"error": "gift not found"}, 404