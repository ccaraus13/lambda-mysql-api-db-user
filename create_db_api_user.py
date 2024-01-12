import sys
import logging
from logging import StreamHandler, FileHandler

import pymysql
import json
import os
import urllib3
from urllib3 import Timeout

# call in aws:
# create_api_user.handler

#  mysql -u petclinic -p --host 127.0.0.1 --port 3313
# jdbc:mysql://localhost/petclinic

api_user_role = "api_user_role"

http = urllib3.PoolManager()

logging_level_str = os.environ.get('PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL', "INFO").upper()
logging_level = logging.getLevelName(logging_level_str)

# logging.basicConfig(handlers=[StreamHandler(), FileHandler(filename="logs")])
logging.basicConfig(handlers=[StreamHandler()])
logger = logging.getLogger()

logger.setLevel(logging_level)
urllib3.add_stderr_logger(logging_level)


def handler(event, context):
    """
    Invoked by AWS as create_db_api_user.handler
    1. Get DB `root`(master) credentials from AWS Secret Manager by provided `DB_ROOT_SECRET_ID`
    2. Connects to DB using  DB `root`(master) credentials
    3. Get DB `db_user_api` credentials from AWS Secret Manager by provided `DB_API_USER_SECRET_ID`
    4. Drop `db_user_api` (if exists) and creates a new user using provided credentials. Provide grants
    5. Tests connection with new created user. I test fails user is dropped
    Connects to DB using `root` credentials got from received
    :param event: must contain a JSON,
            eg: {"DB_ROOT_SECRET_ID": "root_secret", "DB_API_USER_SECRET_ID": "api_secret", "DB_HOST": "localhost", "DB_PORT": 3313}
    :param context:
    :return: success message in JSON, or exception is thrown
    """
    logger.info("Event: %s", event)
    db_root_secret_id = event['DB_ROOT_SECRET_ID']
    db_api_user_secret_id = event['DB_API_USER_SECRET_ID']

    db_root_connection = retrieve_connection_settings(db_root_secret_id)
    # host, port, dbname may not be set in `root` secret(if managed by RDS itself)
    db_root_connection.host = event['DB_HOST']
    db_root_connection.port = event['DB_PORT']

    logger.info("DB Root Connection Settings: %s", db_root_connection)

    with get_db_connection(db_root_connection) as connection:
        db_api_connection = retrieve_connection_settings(db_api_user_secret_id)
        logger.info("DB Api User Connection Settings: %s", db_api_connection)

        # manage_role(connection, api_user_role, db_api_connection.dbname)
        manage_api_user(connection, db_api_connection.username, db_api_connection.password, db_name=db_api_connection.dbname)

        connection.commit()

        try:
            test_connection(db_api_connection)
        except pymysql.MySQLError as exception:
            logger.error("Unexpected error: Could not connect to MySQL instance. Cleanup fresh created user`%s`", db_api_connection.username)
            logger.error(exception)

            drop_user(connection,  db_api_connection.username)
            connection.commit()
            raise exception

    logger.info("Success, user %s created", db_api_connection.username)

    return {
        "status": "OK",
        "username": db_api_connection.username,
        "secret_id": db_api_user_secret_id
    }


class DbConnectionSettings:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(host=args[0].get('host', None),
                          port=args[0].get('port', 3306),
                          username=args[0].get('username', None),
                          password=args[0].get('password', None),
                          dbname=args[0].get('dbname', None))
        return instance

    def __init__(self, host=None, port=3306, username=None, password=None, dbname=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname

    def __repr__(self) -> str:
        return f"host={self.host}, port={self.port}, username={self.username}, password=****, dbname={self.dbname}"


def get_db_connection(db_connection: DbConnectionSettings):
    try:
        return pymysql.connect(host=db_connection.host,
                               port=db_connection.port,
                               user=db_connection.username,
                               passwd=db_connection.password,
                               db=db_connection.dbname,
                               connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()


def retrieve_connection_settings(secret_id):
    """
    Define function to retrieve values from extension local HTTP server cache
    :param secret_id:
    :return:
    """
    try:
        secret_path = "/secretsmanager/get?secretId=%s" % secret_id
        secret_port_service = os.environ.get('PARAMETERS_SECRETS_EXTENSION_HTTP_PORT', "2773")
        url = ('http://localhost:' + secret_port_service + secret_path)
        headers = { "X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN', "") }
        response = http.request(method="GET", url=url, headers=headers, retries=False, timeout=Timeout(10))
        # logger.debug(response.data)
        secret_string = json.loads(response.data)['SecretString']

        return DbConnectionSettings.__new__(DbConnectionSettings, json.loads(secret_string))
    except Exception as exception:
        logger.error("failed getting secret by id")
        logger.error(exception)
        raise exception


def manage_role(connection, api_role_name, db_name):
    """
    $ create role if not exists 'api_user_role';
    $ grant alter,create,delete,drop,index,insert,select,update,trigger,alter routine, create routine, execute, create temporary tables on petclinic.* to 'api_user_role';

    :param connection:
    :param api_role_name:
    :param db_name:
    :return:
    """
    if not exists_user_or_role(connection, api_role_name):
        create_api_user_role(connection, api_role_name)
        grant_all(connection, db_name, api_role_name)
    else:
        revoke_all(connection, api_role_name)
        grant_all(connection, db_name, api_role_name)


def manage_api_user(connection, api_db_username, api_db_username_pass, db_name, role_name=None):
    """
    $ drop user if exists 'petdbuser';
    $ create user 'petdbuser' IDENTIFIED BY 'petdbpass' default role 'api_user_role';
    :param connection:
    :param api_db_username:
    :param api_db_username_pass:
    :param role_name:
    :param db_name:
    :return:
    """
    drop_user(connection, api_db_username)
    # create_user_with_role(connection, api_db_username, api_db_username_pass, role_name)
    create_user(connection, api_db_username, api_db_username_pass)
    grant_all(connection, db_name, api_db_username)


def drop_user(connection, username):
    with connection.cursor() as cursor:
        sql = "DROP USER IF EXISTS '%s'" % username
        cursor.execute(sql)


def revoke_all(connection, username):
    with connection.cursor() as cursor:
        sql = "REVOKE ALL ON *.* FROM %s@'%%' IGNORE UNKNOWN USER" % username
        cursor.execute(sql)


def create_api_user_role(connection, role_name):
    with connection.cursor() as cursor:
        sql = "CREATE ROLE IF NOT EXISTS '%s' " % role_name
        cursor.execute(sql)


def exists_user_or_role(connection, username):
    with connection.cursor() as cursor:
        sql = "SELECT count(1) FROM mysql.user where USER = '%s'" % username
        cursor.execute(sql)
        return cursor.fetchone()[0] > 0


def create_user_with_role(connection, username, password, role_name):
    with connection.cursor() as cursor:
        sql = "CREATE USER '%s' IDENTIFIED BY '%s' DEFAULT ROLE '%s'" % (username, password, role_name)
        cursor.execute(sql)


def create_user(connection, username, password):
    with connection.cursor() as cursor:
        sql = "CREATE USER '%s' IDENTIFIED BY '%s' " % (username, password)
        cursor.execute(sql)


def grant_all(connection, db_name, role_name):
    with connection.cursor() as cursor:
        sql = ("grant alter,create,delete,drop,index,"
               "insert,select,update,trigger,alter routine, "
               "create routine, execute, create temporary tables "
               "on %s.* to '%s' ") % (db_name, role_name)
        cursor.execute(sql)


def test_connection(db_connection: DbConnectionSettings):
    """
    Test connection: creates a new connection and closes it immediately.
    Throws exception if connection failed
    :param db_connection:
    :return:
    """
    # TODO run additional dummy query: SELECT now()
    get_db_connection(db_connection).close()

