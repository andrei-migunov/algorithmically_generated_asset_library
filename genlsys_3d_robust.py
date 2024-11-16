import random
import os

def generate_l_system(axiom, rules, iterations, stochastic=False):
    l_system_string = axiom
    for _ in range(iterations):
        next_string = ""
        for char in l_system_string:
            if stochastic and char in rules and isinstance(rules[char], list):
                next_string += random.choice(rules[char])
            else:
                next_string += rules.get(char, char)
        l_system_string = next_string
    return l_system_string

def generate_param_l_system(axiom, rules, iterations, stochastic=False):
    l_system_string = axiom
    for _ in range(iterations):
        next_string = ""
        i = 0
        while i < len(l_system_string):
            char = l_system_string[i]
            if char in rules:
                params = ""
                if l_system_string[i + 1] == '(':
                    i += 1
                    while l_system_string[i] != ')':
                        params += l_system_string[i]
                        i += 1
                    params += ')'
                if stochastic and isinstance(rules[char], list):
                    rule = random.choice(rules[char])
                else:
                    rule = rules[char]
                next_string += rule.format(*params.strip('()').split(',')) if params else rule
            else:
                next_string += char
            i += 1
        l_system_string = next_string
    return l_system_string

# Parameterized L-system configurations
param_l_systems = [
    {
        "name": "ParametricPlant",
        "axiom": "F(1)",
        "rules": {
            "F(x)": "F({0}*1.1)[+F({0}*0.7)]F({0}*0.7)[-F({0}*0.7)]F({0}*0.7)"
        },
        "iterations": 4,
        "stochastic": False
    },
    {
        "name": "ParametricTree",
        "axiom": "A(1,10)",
        "rules": {
            "A(l,w)": "!(w)F(l)[&(45)A({0}/2,{1}*0.707)]/(120)[&(45)A({0}/2,{1}*0.707)]/(120)[&(45)A({0}/2,{1}*0.707)]"
        },
        "iterations": 5,
        "stochastic": False
    },
    {
        "name": "StochasticParametricTree",
        "axiom": "F(1)",
        "rules": {
            "F(x)": ["F({0}*1.05)[+F({0}*0.7)]F({0}*0.7)[-F({0}*0.7)]F({0}*0.7)", "F({0}*1.1)[-F({0}*0.8)]F({0}*0.8)[+F({0}*0.8)]F({0}*0.8)"]
        },
        "iterations": 4,
        "stochastic": True
    }
]

# Non-parameterized L-system configurations
l_systems = [
    {
        "name": "FractalPlant",
        "axiom": "X",
        "rules": {
            "X": "F+[[X]-X]-F[-FX]+X",
            "F": "FF"
        },
        "iterations": 5,
        "stochastic": False
    },
    {
        "name": "BinaryTree",
        "axiom": "0",
        "rules": {
            "1": "11",
            "0": "1[0]0"
        },
        "iterations": 6,
        "stochastic": False
    },
    {
        "name": "DragonCurve",
        "axiom": "FX",
        "rules": {
            "X": "X+YF+",
            "Y": "-FX-Y"
        },
        "iterations": 10,
        "stochastic": False
    },
    {
        "name": "KochCurve",
        "axiom": "F",
        "rules": {
            "F": "F+F-F-F+F"
        },
        "iterations": 4,
        "stochastic": False
    },
    {
        "name": "SierpinskiTriangle",
        "axiom": "A",
        "rules": {
            "A": "B-A-B",
            "B": "A+B+A"
        },
        "iterations": 7,
        "stochastic": False
    },
    {
        "name": "HilbertCurve",
        "axiom": "A",
        "rules": {
            "A": "-BF+AFA+FB-",
            "B": "+AF-BFB-FA+"
        },
        "iterations": 5,
        "stochastic": False
    },
    {
        "name": "PeanoCurve",
        "axiom": "X",
        "rules": {
            "X": "XFYFX+F+YFXFY-F-XFYFX",
            "Y": "YFXFY-F-XFYFX+F+YFXFY"
        },
        "iterations": 3,
        "stochastic": False
    },
    {
        "name": "CantorSet",
        "axiom": "A",
        "rules": {
            "A": "ABA",
            "B": "BBB"
        },
        "iterations": 4,
        "stochastic": False
    },
    {
        "name": "StochasticPlant",
        "axiom": "X",
        "rules": {
            "X": ["F-[[X]+X]+F[+FX]-X", "F-[[X]+X]+F[+FX]+X"],
            "F": "FF"
        },
        "iterations": 5,
        "stochastic": True
    },
    {
        "name": "RandomTree",
        "axiom": "X",
        "rules": {
            "X": ["F[+X]F[-X]+X", "F[-X]+X"],
            "F": "FF"
        },
        "iterations": 6,
        "stochastic": True
    },
    {
        "name": "BushyTree",
        "axiom": "X",
        "rules": {
            "X": "F[+X][-X]FX",
            "F": "FF"
        },
        "iterations": 6,
        "stochastic": False
    },
    {
        "name": "SpiralTree",
        "axiom": "X",
        "rules": {
            "X": "F[+X]F[-X]FX",
            "F": "FF"
        },
        "iterations": 5,
        "stochastic": False
    }
]

# Generate L-systems and save to text files
output_dir = "C:\\Users\\andre\\Dropbox\\Code\\Tree_Render\\LSystems"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generate non-parameterized L-systems
for l_system in l_systems:
    l_system_string = generate_l_system(l_system["axiom"], l_system["rules"], l_system["iterations"], l_system["stochastic"])
    file_suffix = "stochastic" if l_system["stochastic"] else "deterministic"
    file_path = os.path.join(output_dir, f"{l_system['name']}_{file_suffix}.txt")
    with open(file_path, "w") as file:
        file.write(l_system_string)
    print(f"Generated {file_suffix} L-system for {l_system['name']} and saved to {file_path}")

# Generate parameterized L-systems
for l_system in param_l_systems:
    l_system_string = generate_param_l_system(l_system["axiom"], l_system["rules"], l_system["iterations"], l_system["stochastic"])
    file_suffix = "stochastic" if l_system["stochastic"] else "deterministic"
    file_path = os.path.join(output_dir, f"{l_system['name']}_{file_suffix}.txt")
    with open(file_path, "w") as file:
        file.write(l_system_string)
    print(f"Generated {file_suffix} parameterized L-system for {l_system['name']} and saved to {file_path}")
