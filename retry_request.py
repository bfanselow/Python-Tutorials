"""
  A useful RETRY requests utility

  Here's an example of how we might use the utility

  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  TARGET_SERVER = environ.get("TARGET_SERVER", "https://myserver.test.com")
  API_TOKEN = environ.get(“API_TOKEN")

  class MyCustomException(Exception):
      pass

  def my_retry_request(verb, endpoint, api_version="v3", headers=None):
      if not headers:
          headers = {}
      if "X-Forwarded-User" not in headers:
          headers["X-Forwarded-User"] = platform.node()

      url = "%s/%s/%s" % (TARGET_SERVER, api_version, api_endpoint)

      try:
          request = getattr(requests_retry_session(custom_exception=MyCustomException), verb)
          http_response = request(url, headers=headers, **kwargs)
      except MyCustomException as exc:
          try:
              err_msg = http_response.json().get("message")
          except Exception:
              raise exc
          else:
              raise MyCustomException(err_msg)

      return http_response.json()


  if __name == '__main__':
      resp_json = my_retry_request('get', 'some_fake_api_endpoint')
      print(resp_json)
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# https://docs.python-requests.org/en/latest/user/advanced/#timeouts
DEFAULT_TIMEOUT = (
    3.1,  # connection time
    15,  # read timeout (Time to first byte)
)

class CustomHTTPAdapter(HTTPAdapter):
    def __init__(self, custom_exception=None, *args, **kwargs):
        self.custom_exception = custom_exception
        super(CustomHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        if not kwargs.get("timeout"):
            kwargs["timeout"] = DEFAULT_TIMEOUT
        try:
            return super(CustomHTTPAdapter, self).send(request, **kwargs)
        except requests.exceptions.HTTPError as exc:
            if self.custom_exception:
                raise self.custom_exception("HTTP Error: %s" % exc)
            else:
                raise exc
        except requests.exceptions.ConnectionError as exc:
            if self.custom_exception:
                raise self.custom_exception("Connection Error: %s" % exc)
            else:
                raise exc
        except requests.exceptions.Timeout as exc:
            if self.custom_exception:
                raise self.custom_exception("Timeout Error: %s" % exc)
            else:
                raise exc
        except requests.exceptions.RequestException as exc:
            if self.custom_exception:
                raise self.custom_exception("Request Exception: %s" % exc)
            else:
                raise exc


def raise_request_exception(resp, custom_exception=None, *args, **kwargs):
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        if custom_exception:
            raise custom_exception("HTTP Error: %s" % exc)
        else:
            raise exc
    except requests.exceptions.ConnectionError as exc:
        if custom_exception:
            raise custom_exception("Connection Error: %s" % exc)
        else:
            raise exc
    except requests.exceptions.Timeout as exc:
        if custom_exception:
            raise custom_exception("Timeout Error: %s" % exc)
        else:
            raise exc
    except requests.exceptions.RequestException as exc:
        if custom_exception:
            raise custom_exception("Request Exception: %s" % exc)
        else:
            raise exc


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    raise_exception=True,
    custom_exception=None,
):
    session = requests.Session()

    if raise_exception:
        if custom_exception:
            session.hooks["response"].append(
                lambda resp, *args, **kwargs: raise_request_exception(
                    resp, custom_exception=custom_exception, *args, **kwargs
                )
            )
        else:
            session.hooks["response"].append(raise_request_exception)

    # Retry on failure
    adapter = CustomHTTPAdapter(
        custom_exception=custom_exception,
        max_retries=Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        ),
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


