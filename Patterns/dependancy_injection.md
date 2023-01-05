## Dependancy Injection

shout out to Roman Mogylatov, who authored the article from which much of this is drawn - https://python-dependency-injector.ets-labs.org/introduction/di_in_python.html

---

#### Dependency injection is a principle that helps to decrease "Coupling" and increase "Cohesion".


Coupling and cohesion basically characterize how tough the components are tied together.

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

Notice how ```ApiClient``` is now decoupled from knowing where the options come from. You can read a key and a timeout from a configuration file, or get them from a database. ```Service``` is now decoupled from the ```ApiClient```. Since it does not create it, you can provide a stub or other compatible object. And ```main()``` is now decoupled from ```Service```, receiving it as an argument.

#### Everything comes with a cost
The drawback is that now you have to assemble the objects to be injected (i.e. the "service" object passed in main above).  This object assembly code might get duplicated. Over time, it will likely become harder to change the application structure.

### Dependancy Injector
The solution to this is the ***Dependency Injector*** which will assemble and inject the dependencies.


