"""

A Mixin is a set of properties and methods that can be used in different classes, which don't
come from a base class. In Object Oriented Programming languages, you typically use inheritance
to give objects of different classes the same functionality; if a set of objects have some ability,
you put that ability in a base class that both objects inherit from.

For instance, say you have the classes Car, Boat, and Plane. Objects from all of these classes have
the ability to travel, so they get the function travel. In this scenario, they all travel the same
basic way, too; by getting a route, and moving along it.

To implement this functionality, you could derive all of the classes from Vehicle, and put the
function in that shared class:

```
class Vehicle(object):
   """A generic vehicle class."""

   def __init__(self, position):
       self.position = position

   def travel(self, destination):
       route = calculate_route(from=self.position, to=destination)
       self.move_along(route)

class Car(Vehicle):
   ...

class Boat(Vehicle):
   ...

class Plane(Vehicle):
   ...
```

With this code, you can call travel on a car (car.travel("Montana")), boat (boat.travel("Hawaii")),
and plane (plane.travel("France"))

However, what if you have functionality that's not available to a base class?
For example, you want to give Car a radio and the ability diver and passengers to play a song on a
radio station, with play_song_on_station(). Suppose you also have a Clock that can use a radio too
but Car and Clock inherit from different base classes.

Suppose the Boat and Plane objects (at least in this example) don't want to allow the user to play the radio.
So how do you accomplish without duplicating code? You can use a mixin. In Python, giving a class a mixin is
as simple as adding it to the list of subclasses, like this

```
class Foo(main_super, mixin):
   ...

Foo will inherit all of the properties and methods of main_super, but also those of mixin as well.

So, to give the classes Car and clock the ability to use a radio, you could override Car from the last example
and write this:

class UserRadioMixin(object):
   def __init__(self):
       self.radio = Radio()

   def play_song_on_station(self, station):
       self.radio.set_station(station)
       self.radio.play_song()

class Car(Vehicle, UserRadiorMixin): # in Python the classname appended by "Mixin" is convention for a mixin class.
   ...


class Clock(Machine, UserRadioMixin):
   ...
```

Now you can call car.play_song_on_station(98.7) and clock.play_song_on_station(101.3), but not something like
boat.play_song_on_station(100.5)

The important thing with mixins is that they allow you to add functionality to much different objects which
don't share a "main" subclass with this functionality but still share the code for it nonetheless.
Without mixins, doing something like the above example would be much harder, and/or might require
some repetition. Both the Boat and Plane class could inerhit PortLightMixin and StarboardLightMixin which
provided functionality for flashing red and green lights for the left/right side of the vehicle.

