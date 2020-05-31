class Robot:
    """
    The Robot class has a publically avaialable 'condition' attribute
    which depends on multiple private attributes.
    Since its value is conditional, we make it a property .
    """
    def __init__(self, name, build_year, ps = 0.5, ms = 0.5 ):
        self.name = name
        self.build_year = build_year
        self.__physical_state = ps
        self.__mental_state = ms

    @property
    def condition(self):
        s = self.__physical_state + self.__mental_state
        if s <= -1:
           return "I feel miserable!"
        elif s <= 0:
           return "I feel bad!"
        elif s <= 0.5:
           return "Could be worse!"
        elif s <= 1:
           return "Seems to be okay!"
        else:
           return "Great!" 
  
if __name__ == "__main__":
    x = Robot("Bill", 1979, 0.2, 0.4 )
    y = Robot("John", 1993, -0.4, 0.3)
    print(x.condition)
    print(y.condition)
