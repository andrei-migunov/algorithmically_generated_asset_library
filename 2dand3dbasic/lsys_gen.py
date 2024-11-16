import math

class LSystem:
    def __init__(self, axiom, rules, angle, iterations):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle
        self.iterations = iterations
        self.sentence = axiom

    def generate(self):
        for _ in range(self.iterations):
            next_sentence = ""
            for char in self.sentence:
                next_sentence += self.rules.get(char, char)
            self.sentence = next_sentence

    def get_sentence(self):
        return self.sentence

# Example L-system (Fractal Tree)
axiom = "F"
rules = {
    "F": "FF+[+F-F-F]-[-F+F+F]"
}
angle = 25.7
iterations = 3


# axiom = "X"
# rules = {
#     "X": "F+[[X]-X]-F[-FX]+X", "F":"FF"
# }
# angle = 25.7
# iterations = 3


lsystem = LSystem(axiom, rules, angle, iterations)
lsystem.generate()
print(lsystem.get_sentence())

# Write it to a file
with open("lsystem.txt", "w") as file:
    file.write(lsystem.get_sentence())
