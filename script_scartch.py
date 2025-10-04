# from google import genai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Explain how AI works in a few words",
# )

# print(response.text)

import math
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def ask_llm(prompt):
    response = client.models.generate_content(
        model ="gemini-2.5-flash",
        contents = prompt
    )
    return response.text

#----------------------------------------------------------------------------------
def add(x, y):
    return x + y
def subtract(x, y):
    return x - y
def multiply(x, y):
    return x * y
def divide(x, y):
    if y == 0:
        return "Error! Division by zero."
    else:
        return x / y
def power(x, y):
    return math.pow(x, y)
def square_root(x):
    if x < 0:
        return "Error! Negative number cannot have a real square root."
    return math.sqrt(x)
def logarithm(x):
    if x <= 0:
        return "Error! Logarithm undefined for zero or negative numbers."
    return math.log10(x)
def sine(x):
    return math.sin(math.radians(x))
def cosine(x):
    return math.cos(math.radians(x))
def tangent(x):
    return math.tan(math.radians(x))

#----------------------------------------------------------------------------------

#**args is used to pass a variable number of keyword arguments to a function. its like a dicionary
def calculate(operator, **args):
    if "y" in args:
        return eval(f"{operator}({args['x']}, {args['y']})")
    else:
        return eval(f"{operator}({args['x']})")
    
def search(query):
    # Mock search tool
    return f"Search result for '{query}'"

def call_tool(tool, params):
    if tool.lower() == "calculator":
        return calculate(**params)
    elif tool.lower() == "search":
        return search(params['query'])
    else:
        return "Unknown tool"
    
#----------------------------------------------------------------------------------

def scratch_agent(question, max_steps=5):
    history = []
    step = 0

    while step < max_steps:
        prompt = f"""
            You are a reasoning agent. Solve the question using the available tools.
            Tools: calculator (add, subtract, multiply, divide, power, square_root, log, sine, cosine, tangent), search (query)
            History:
            {chr(10).join(history)}
            Question: {question}
            Thought:"""
        response = ask_llm(prompt)
        print(f"LLM Response:\n{response}\n")

        # Check for final answer
        if "Final Answer:" in response:
            final = response.split("Final Answer:")[-1].strip()
            print(f"\n Final Answer: {final}")
            return final

        # Try to parse tool usage
        if "Action:" in response and "Action Input:" in response:
            try:
                tool_line = [line for line in response.split("\n") if "Action:" in line][0]
                input_line = [line for line in response.split("\n") if "Action Input:" in line][0]

                tool_name = tool_line.split("Action:")[-1].strip()
                inputs = input_line.split("Action Input:")[-1].strip().split(",")

                params = {}
                # For calculator, first param is func
                if tool_name.lower() == "calculator":
                    params["operator"] = inputs[0].strip()
                    params["x"] = float(inputs[1].strip())
                    if len(inputs) > 2:
                        params["y"] = float(inputs[2].strip())
                elif tool_name.lower() == "search":
                    params["query"] = inputs[0].strip()

                observation = call_tool(tool_name, params)
                history.append(f"{response}\nObservation: {observation}\nThought:")
                step += 1

            except Exception as e:
                print("Error parsing action:", e)
                history.append(response)
                step += 1
        else:
            history.append(response)
            step += 1

    print("error")
    return None


if __name__ == "__main__":
    q1 = "I want to add 2 and 3 then divide by 5."
    scratch_agent(q1)

    q2 = "Alfred buys an old scooter for Rs. 4700 and spends Rs. 800 on repairs. If he sells the scooter for Rs. 5800, his gain percent is:"
    scratch_agent(q2)

