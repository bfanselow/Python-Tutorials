When accessing a JSON api with the Python requests module, there is a nice pattern for handling exceptions in the request and response, to verify a successful API interaction and handle errors which may be produced at various layers.

1) Use try/catch for sending the request (catches errors at the network level)
2) Use raise_for_response() in the same try block to validate the HTTP response code. (catches errors at the HTTP protocol level). Whenever we make a request to a specified URI through Python, it returns a response object.
response.raise_for_status() returns an HTTPError object if an error has occurred during the process.  The HTTPError is inherited from RequestException
https://requests.readthedocs.io/en/latest/_modules/requests/exceptions/

3) Verify that the response is valid json before unpacking the JSON (catches errors at the API/encoding level)
4) Unpack the json and look for content indicating successful application behavior (catches errors at the application level)

**EXAMPLE method does performs an API request**
```
from requests.exceptions import RequestException
from requests.exceptions import JSONDecodeError

class ApiResponseError(Exception):
    pass

def api_update_method(data):
   url = "http://my.url.com"
   endpoint = "api/public/myapi"
    try:  # (1)
        resp = requests_retry_session().put(
            f"{url}/{endpoint}",
            data={"row_data": data},  # pass in a python dict
        )
        resp.raise_for_status() # (2); this will raise HTTPError which inherits from RequestException
    except RequestException as e:
        throw ApiResponseError(f"Error updating API: {str(e)}")

    resp_data = None
    try:
        resp_data = resp.json() # (3)
    except JSONDecodeError:
         throw ApiResponseError(f"Response did not contain valid JSON {resp.text}")

     # Suppose our expected response is {"success": true, "message": "Record was updated"}
     if not resp_data.get("success"):  # (4)
        throw ApiResponseError(resp_data.get("message") or str(resp_data))

    return resp_data.get("message")
```

**Example CALLER for this api method**
```
from .api import ApiResponseError

class ApiUpdateError(Exception)
data = {
        "name": "fanselow",
        "birthdate": birth_date,
}
try:
    api_put( )
except ApiResponseError as e:
        raise ApiUpdateError(f"Failed to update: {str(data)}: {str(e)}")
```
