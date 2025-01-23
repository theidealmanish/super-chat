import os
from snowflake.snowpark import Session
from snowflake.core import Root
from dotenv import load_dotenv

load_dotenv()

# service parameters
CONNECTION_PARAMS = {
    "account": os.environ.get("SNOWFLAKE_ACCOUNT"),
    "user": os.environ.get("SNOWFLAKE_USER"),
    "password": os.environ.get("SNOWFLAKE_USER_PASSWORD"),
    "role": os.environ.get("SNOWFLAKE_ROLE"),
    "database": os.environ.get("SNOWFLAKE_DATABASE"),
    "schema": os.environ.get("SNOWFLAKE_SCHEMA"),
    "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE"),
    "search_service": os.environ.get("SNOWFLAKE_CORTEX_SEARCH_SERVICE"),
    "client_session_keep_alive": True
}


SESSION = Session.builder.configs(CONNECTION_PARAMS).create()
SVC = Root(SESSION).databases[CONNECTION_PARAMS["database"]].schemas[CONNECTION_PARAMS["schema"]
                                                                     ].cortex_search_services[CONNECTION_PARAMS["search_service"]]
