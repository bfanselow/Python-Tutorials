## Dependancy Injection

shout out to Roman Mogylatov, who authored the article from which much of this is drawn - https://python-dependency-injector.ets-labs.org/introduction/di_in_python.html

---

#### Dependency injection is a coding pattern that can help you write loosely-coupled, highly-cohesive code.


Coupling and cohesion basically characterize how tough the components are tied together.

 * **High coupling**: High coupling is like using glue. There is no easy way to disassemble components.

 * **High cohesion**: High cohesion is like using screws. Opposite of high coupling, its easy to disassemble and re-assemble (perhpas in a different way). 

Cohesion often correlates with coupling. Higher cohesion usually leads to lower coupling and vice versa.

![image](https://user-images.githubusercontent.com/24737190/210669149-ef4f7d37-c390-4e95-921c-a943839a6de0.png)

Low coupling increases flexibility and makes your code easir to change and test.

#### So how do we implement dependency injection?

Dependency Injection is a technique in which an object *receives* other objects that it depends on, rather than *creating* them.

In general, do not construct objects that **create** other objects (dependancies). Provide a way to inject the dependancies instead.

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

With the dependency injection pattern, objects lose the responsibility of assembling the dependencies. The Dependency Injector absorbs that responsibility.

Dependency Injector helps to assemble and inject the dependencies.

It provides a container and providers that help you with the objects assembly. When you need an object you place a Provide marker as a default value of a function argument. When you call this function, framework assembles and injects the dependency.

```
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    api_client = providers.Singleton(
        ApiClient,
        api_key=config.api_key,
        timeout=config.timeout,
    )

    service = providers.Factory(
        Service,
        api_client=api_client,
    )

@inject
def main(service: Service = Provide[Container.service]) -> None:
    ...

if __name__ == "__main__":
    container = Container()
    container.config.api_key.from_env("API_KEY", required=True)
    container.config.timeout.from_env("TIMEOUT", as_=int, default=5)
    container.wire(modules=[__name__])

    main()  # <-- dependency is injected automatically

    with container.api_client.override(mock.Mock()):
        main()  # <-- overridden dependency is injected automatically
```

When you call the main() function the Service dependency is assembled and injected automatically.

When you do testing, you call the container.api_client.override() method to replace the real API client with a mock. When you call main(), the mock is injected.

You can override any provider with another provider.

It also helps you in a re-configuring project for different environments: replace an API client with a stub on the dev or stage.

Objects assembling is consolidated in a container. Dependency injections are defined explicitly. This makes it easier to understand and change how an application works.

#### Testing, Monkey-patching and dependency injection
In Python, you can monkey-patch anything, anytime. The problem with monkey-patching is that it’s too fragile. The cause of it is that when you monkey-patch you do something that wasn’t intended to be done. You monkey-patch the implementation details. When implementation changes the monkey-patching is broken.

With dependency injection, you patch the interface, not an implementation - a much more stable approach.

Also, monkey-patching is way too dirty to be used outside of the testing code for re-configuring the project for the different environments.

#### Summary
Dependency injection provides you with three advantages:

 * Flexibility. The components are loosely coupled. You can easily extend or change the functionality of a system by combining the components in a different way. You even can do it on the fly.

 * Testability. Testing is easier because you can easily inject mocks instead of real objects that use API or database, etc.

 * Clearness and maintainability. Dependency injection helps you reveal the dependencies. Implicit becomes explicit. And “Explicit is better than implicit” (PEP 20 - The Zen of Python). You have all the components and dependencies defined explicitly in a container. This provides an overview and control of the application structure. It is easier to understand and change it.
