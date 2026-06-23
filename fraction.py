class fraction:
    
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator
    

    def simplify(other):
        GCD=1

        for i in range(1,int(min(other.numerator,other.denominator)/2)+1):
            if other.numerator % i == 0 and other.denominator % i == 0:
                GCD = i

        return fraction(other.numerator // GCD, other.denominator // GCD)


    def __str__(self):
        return f"Your Fraction is {self.numerator}/{self.denominator}"
    
    def add_fraction(self,other):
        if not (isinstance(other,fraction) or isinstance(other,int)):
            return "Can only add fractions or integers"

        if isinstance(other, int):
            other = fraction(other, 1)

        new_denominator=self.denominator*other.denominator
        new_numerator=(new_denominator/self.denominator)*self.numerator + (new_denominator/other.denominator)*other.numerator
        return self.simplify(fraction(int(new_numerator), int(new_denominator)))
    
    def multiply_fraction(self,other):
        if not (isinstance(other,fraction) or isinstance(other,int)):
            return "Can only multiply fractions or integers"

        if isinstance(other, int):
            other = fraction(other, 1)

        new_numerator = self.numerator * other.numerator
        new_denominator = self.denominator * other.denominator
        return self.simplify(fraction(int(new_numerator), int(new_denominator)))

    def divide_fraction(self,other):
        if not (isinstance(other,fraction) or isinstance(other,int)):
            return "Can only divide fractions or integers"

        if isinstance(other, int):
            other = fraction(other, 1)

        new_numerator = self.numerator * other.denominator
        new_denominator = self.denominator * other.numerator
        return self.simplify(fraction(int(new_numerator), int(new_denominator)))

    def subtract_fraction(self,other):
        if not (isinstance(other,fraction) or isinstance(other,int)):
            return "Can only subtract fractions or integers"

        if isinstance(other, int):
            other = fraction(other, 1)

        new_denominator = self.denominator * other.denominator
        new_numerator = (new_denominator / self.denominator) * self.numerator - (new_denominator / other.denominator) * other.numerator
        return self.simplify(fraction(int(new_numerator), int(new_denominator)))
