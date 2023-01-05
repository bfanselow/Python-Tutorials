## Dependancy Injection

(many concepts pulled from https://python-dependency-injector.ets-labs.org/introduction/di_in_python.html by Roman Mogylatov)

--

#### Dependency injection is a coding pattern that can help you write loosely-coupled, highly-cohesive code.


Coupling and cohesion basically characterize how tightly the components are tied together.

 * **High coupling**: High coupling is like using glue. There is no easy way to disassemble components.

 * **High cohesion**: High cohesion is like using screws. Opposite of high coupling, its easy to disassemble and re-assemble (perhaps in a different way). 

Cohesion often correlates with coupling. Higher cohesion usually leads to lower coupling and vice versa.

![image](https://user-images.githubusercontent.com/24737190/210669149-ef4f7d37-c390-4e95-921c-a943839a6de0.png)

Low coupling increases flexibility, makes your code cleaner, easier to understand and simpler to extend and test.

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

With the dependency injection pattern, objects lose the responsibility of assembling the dependencies. The Dependency Injector takes responsibility for helping to assemble and inject the dependencies.

The Dependancy Injector provides a **Container** and **Providers** that help you with object assembly. When you need an object you place a Provide marker as a default value of a function argument. When you call this function, the framework assembles and injects the dependency.

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
In Python, you can monkey-patch anything, anytime. The problem with monkey-patching is that it’s fragile. since you are monkey-patching the implementation details. When implementation changes the monkey-patching is broken. With dependency injection, you patch the interface, not an implementation - a much more stable approach. Methods are easier to test. Dependencies are easier to mock. And tests don't have to change every time twe extend our application.

#### Summary
Dependency injection provides you with several advantages:

 * **Clarity**: Dependency injection helps you reveal the dependencies.  “Explicit is better than implicit”. You have all the components and dependencies defined explicitly in a container, giving you an overview and control of the application's structure. It's simply easier to understand the system.

 * **Testability**: Testing is easier as you can easily inject mock objects instead of real objects.

 * **Maintainability and extendability**: The above benefits, combined with the flexibility of a loosely coupled system, result in a system that is easier to maintain and extend.  You can even change the functionality of the system by combining the components in different ways on the fly.
