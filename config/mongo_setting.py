from config.setting import BaseAppSettings


class MongoSetting(BaseAppSettings):
    mongodb_conn_serv: str
    mongodb_host: str
    mongodb_port: int
    mongodb_db: str
    mongodb_id: str
    mongodb_pw: str
    mongodb_client: str
    mongodb_log: str
    connection_timeout_ms: int
    socket_timeout_ms: int
    server_selection_timeout_ms: int
    reload_period: int
    query_string: str
