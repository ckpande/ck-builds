# http_client.py
# Chandrakant Pande - ckpande
import atexit
import logging
import threading
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from retry import retry

log = logging.getLogger(__name__)

_local = threading.local()


def _get_session() -> requests.Session:
    if not hasattr(_local, "session"):
        session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=0)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        _local.session = session
        atexit.register(session.close)
    return _local.session


@retry(attempts=3, delay=0.5, backoff=2.0)
def http_get(url: str, timeout: float = 10.0, **kwargs: Any) -> requests.Response:
    log.debug("GET %s", url)
    response = _get_session().get(url, timeout=timeout, **kwargs)
    response.raise_for_status()
    return response


@retry(attempts=3, delay=0.5, backoff=2.0)
def http_post(
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Any = None,
        timeout: float = 10.0,
        **kwargs: Any
) -> requests.Response:
    log.debug("POST %s", url)
    response = _get_session().post(url, json=json_data, data=data, timeout=timeout, **kwargs)
    response.raise_for_status()
    return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")

    try:
        resp = http_get("https://httpbin.org/get", timeout=5.0)
        print("GET success:", resp.status_code)
    except requests.exceptions.RequestException as e:
        print("GET failed:", e)

    try:
        resp = http_post("https://httpbin.org/post", json_data={"key": "value"}, timeout=5.0)
        print("POST success:", resp.status_code)
    except requests.exceptions.RequestException as e:
        print("POST failed:", e)
