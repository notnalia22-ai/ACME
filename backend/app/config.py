from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    cassandra_hosts: str = "cassandra"
    cassandra_keyspace: str = "financial_dw"

    cassandra_port: int = 9042
    cassandra_dc: str = "datacenter1"

    cassandra_replication_strategy: str = "SimpleStrategy"
    cassandra_replication_factor: int = 1

    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"

    groq_api_key: str = ""

    alphavantage_api_key: str = ""
    alphavantage_base_url: str = "https://www.alphavantage.co/query"

    model_config = {
        "env_file": ".env"
    }

    @property
    def cassandra_hosts_list(self) -> list[str]:
        return [
            h.strip()
            for h in self.cassandra_hosts.split(",")
        ]


settings = Settings()
