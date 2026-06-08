import threading
import time

from cassandra.cluster import Cluster, Session
from cassandra.policies import DCAwareRoundRobinPolicy

from app.config import settings


_cluster = None
_session: Session | None = None
_lock = threading.Lock()


def get_session() -> Session:

    global _cluster, _session

    if _session is None:

        with _lock:

            if _session is None:

                retries = 10
                delay = 5

                for attempt in range(1, retries + 1):

                    try:

                        _cluster = Cluster(
                            settings.cassandra_hosts_list,
                            port=settings.cassandra_port,
                            load_balancing_policy=DCAwareRoundRobinPolicy(
                                local_dc=settings.cassandra_dc
                            ),
                            protocol_version=5,
                        )

                        _session = _cluster.connect(
                            settings.cassandra_keyspace
                        )

                        return _session

                    except Exception as e:

                        if attempt == retries:
                            raise

                        print(
                            f"Cassandra not ready "
                            f"(attempt {attempt}/{retries}): {e}"
                        )

                        time.sleep(delay)

    return _session


def close() -> None:

    global _cluster, _session

    if _cluster is not None:
        _cluster.shutdown()

    _cluster = None
    _session = None
