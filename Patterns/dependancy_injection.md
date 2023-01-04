#### Dependency injection is a principle that helps to decrease coupling and increase cohesion.


Coupling and cohesion are about how tough the components are tied.

 * **High coupling**: High coupling is like using glue. There is no easy way to disassemble components.

 * **High cohesion**: High cohesion is like using screws. Opposite of high coupling, its easy to disassemble and re-assemble (perhpas in a different way). 

Cohesion often correlates with coupling. Higher cohesion usually leads to lower coupling and vice versa.

![image](https://user-images.githubusercontent.com/24737190/210669149-ef4f7d37-c390-4e95-921c-a943839a6de0.png)

Low coupling brings flexibility. Your code becomes easier to change and test.

#### So how do we implement dependency injection?

In general, do not construct objects that **create** other objects (dependncies). Provide a way to inject the dependencies instead.

For example, instead of this:
```
import os

class ApiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("API_KEY")  # <-- dependency
        self.timeout = int(os.getenv("TIMEOUT"))  # <-- dependency

class Service:
    def __init__(self) -> None:
        self.api_client = ApiClient()  # <-- dependency

def main() -> None:
    service = Service()  # <-- dependency
    ...

if __name__ == "__main__":
    main()
```

Try this:
```
import os

class ApiClient:
    def __init__(self, api_key: str, timeout: int) -> None:
        self.api_key = api_key  # <-- dependency is injected
        self.timeout = timeout  # <-- dependency is injected

class Service:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client  # <-- dependency is injected

def main(service: Service) -> None:  # <-- dependency is injected
    ...

if __name__ == "__main__":
    main(
        service=Service(
            api_client=ApiClient(
                api_key=os.getenv("API_KEY"),
                timeout=int(os.getenv("TIMEOUT")),
            ),
        ),
    )
 ```
