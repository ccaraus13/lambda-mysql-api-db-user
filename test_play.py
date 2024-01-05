import sys
import logging
import pymysql
import json
import os
import urllib3

import create_db_api_user
from create_db_api_user import DbConnectionSettings
from create_db_api_user import handler
print(sys.path)
# print(logging.)
# print(pymysql.path)
# print(json.path)
# print(os.path)
# print(urllib3.path)
# create_db_api_user.handler(json.loads(sys.argv[1]), None)

secret_dict = {'DB_ROOT_SECRET_ID': "root_secret", 'DB_API_USER_SECRET_ID': 'api_secret', 'DB_HOST': "localhost", 'DB_PORT': 3313}
root_dict = {'username': "root", 'password': 'develop'}
api_dict = {'username': "meineuser", 'password': 'develop123', 'host': 'localhost', 'port': 3313, 'dbname': 'petclinic'}
ajson = json.dumps(secret_dict)
data = json.loads(ajson)

secret_response = """
{"ARN":"arn:aws:secretsmanager:eu-central-1:133566492045:secret:rds!db-c9b7163d-8045-482b-9dfa-e2a96dc3f6e3-1QmcxB","CreatedDate":"2023-12-28T14:57:31.359Z","Name":"rds!db-c9b7163d-8045-482b-9dfa-e2a96dc3f6e3","SecretBinary":null,"SecretString":"{\\"username\\":\\"root\\",\\"password\\":\\"9#2-:X~c0~\\u003es~f{j16jQ6uRa]l!b\\"}","VersionId":"c593fbd2-274e-421c-8ddc-083371280687","VersionStages":["AWSCURRENT"],"ResultMetadata":{}}
"""

secret_string = json.loads(secret_response)['SecretString']
connection = DbConnectionSettings.__new__(DbConnectionSettings, json.loads(secret_string))

print(connection)

def retrieve_connection_settings_4_test(dict):
    ajson = json.dumps(dict)
    data = json.loads(ajson)

    return DbConnectionSettings.__new__(DbConnectionSettings, data)

# print(data['username'])
# print(data['password'])
# result = handler(data, None)
# print(result)
# db_root_connection = create_db_api_user.retrieve_connection_settings_4_test(create_db_api_user.root_dict)
# print(db_root_connection)
#
# db_api_connection = create_db_api_user.handler(secret_dict, None)
# print(db_api_connection)

# level = "debug".upper()
# levelname = logging.getLevelName(level)
# print(levelname)
# urllib3.add_stderr_logger(levelname)

# result = """{"status": "OK", "username": "{0}"}"""
result = '{{"status": "OK"}, {"username": "{0}"}}'
user = "bbb"
rez_json = json.dumps({
    "status": "OK",
    "username": user
})
print( rez_json )
# print( result.format("bbbbb") )
