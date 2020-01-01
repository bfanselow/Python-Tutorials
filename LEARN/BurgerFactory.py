"""

 Demonstration of teh built-in @classmethod decorator for "class-factory" functionalty.

  >>> from Burger import Burger
  >>> Burger()
  Burger(['beef', 'bun', 'lettuce', 'tomato'])
  >>> Burger.plain()
  Burger(['beef', 'bun'])
  >>> Burger.cheese_burger()
  Burger(['beef', 'bun', 'lettuce', 'tomato', 'cheese'])
  >>> Burger.bacon_cheese_burger()
  Burger(['beef', 'bun', 'lettuce', 'tomato', 'cheese', 'bacon'])
  >>> Burger.bison_burger()
  Burger(['bun', 'lettuce', 'tomato', 'bison'])
  >>> Burger.bison_cheese_burger()
  Burger(['bun', 'lettuce', 'tomato', 'cheese', 'bison'])

"""

class Burger:
    def __init__(self, d_customize=None):

        l_basic_ingredients = [
          'beef',
          'bun',
          'lettuce',
          'tomato'
        ]
        d_substitutions = {
          'bison': 'beef'
        }
        self.ingredients = l_basic_ingredients

        if d_customize:
          if 'add' in d_customize:
            self.ingredients.extend(d_customize['add'])

          if 'hold' in d_customize:
            l_remove = d_customize['hold']
            [ self.ingredients.remove(option) for option in l_remove ]

          if 'subst' in d_customize:
            l_subst = d_customize['subst']
            for option in l_subst:
              if option in d_substitutions:
                self.ingredients.remove(d_substitutions[option])
                self.ingredients.append(option)


    def __repr__(self):
        return f'Burger({self.ingredients!r})'

    @classmethod
    def cheese_burger(cls):
        return cls({'add':['cheese']})

    @classmethod
    def bacon_burger(cls):
        return cls({'add':['bacon']})

    @classmethod
    def bacon_cheese_burger(cls):
        return cls({'add':['cheese', 'bacon']})

    @classmethod
    def plain(cls):
        return cls({'hold':['lettuce', 'tomato']})

    @classmethod
    def bison_burger(cls):
        return cls({'subst':['bison']})

    @classmethod
    def bison_cheese_burger(cls):
        return cls({ 'subst':['bison'], 'add':['cheese']})
