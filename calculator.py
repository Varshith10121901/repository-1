import math
import re

def process_expression(input_string):
    # Convert some natural language to actual math expressions
    input_string = input_string.lower()

    # Replace words with symbols/functions
    input_string = input_string.replace("plus", "+")
    input_string = input_string.replace("minus", "-")
    input_string = input_string.replace("times", "*")
    input_string = input_string.replace("divided by", "/")
    input_string = input_string.replace("square root of", "math.sqrt")
    input_string = input_string.replace("sqrt", "math.sqrt")
    input_string = input_string.replace("power of", "**")
    input_string = input_string.replace("sin", "math.sin")
    input_string = input_string.replace("cos", "math.cos")
    input_string = input_string.replace("tan", "math.tan")
    input_string = input_string.replace("pi", "math.pi")

    # Optional: convert degrees to radians for trig functions
    input_string = re.sub(r'math\.(sin|cos|tan)\(([^)]+)\)', r'math.\1(math.radians(\2))', input_string)

    try:
        result = eval(input_string, {"__builtins__": {}}, {"math": math})
        return f"Result: {result}"
    except Exception as e:
        return f"Sorry, couldn't evaluate that. Error: {e}"

# Continuous loop until user quits
while True:
    user_input = input("Enter a mathematical expression or 'quit' to exit: ")
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    print(process_expression(user_input))
