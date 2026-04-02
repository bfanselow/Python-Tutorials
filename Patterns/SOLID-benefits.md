### Separation of Concerns
#### Good separation of concerns often causes an ironic reduction in complexity
Merging concerns reduces surface area which often feels like a **simpler** design. However, in reality it increases complexity density.
Separating concerns increases surface area, which often feels like a more **complex** design. However, in reality it greatly reduces cognitive load per component.  So, while strict separation of concerns might appear to be an increase in complexity, on the surface, it's actually reducing overall complexity density.  There are enormous benefits of a system with strict separation of concerns:
* Easier to make sense of the system, vs a large monolithic swiss-army knife system, especially for someone new to the system.
* Easier to test - unit testing individual components, mocking external dependencies, is far simpler.
* Easier to extend, refactor etc. - adding to the system, or updating components without having to refactor other components (particularly if all the components are loosely coupled with abstract interfaces)
