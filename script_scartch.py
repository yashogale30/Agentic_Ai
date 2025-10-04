import math
import os
import requests
import re
from google import genai
from dotenv import load_dotenv


load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


#-----------------------------------------
def ask_llm(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text if response else ""
    except Exception as e:
        print("LLM call failed:", e)
        return ""


#-----------------------------------------
# Calculator functions
def add(x, y): return x + y
def subtract(x, y): return x - y
def multiply(x, y): return x * y
def divide(x, y): return "Error! Division by zero." if y==0 else x / y
def power(x, y): return math.pow(x, y)
def square_root(x): return "Error! Negative number." if x<0 else math.sqrt(x)
def logarithm(x): return "Error! Non-positive number." if x<=0 else math.log10(x)
def sine(x): return math.sin(math.radians(x))
def cosine(x): return math.cos(math.radians(x))
def tangent(x): return math.tan(math.radians(x))


def calculate(operator, **args):
    if "y" in args:
        return eval(f"{operator}({args['x']}, {args['y']})")
    else:
        return eval(f"{operator}({args['x']})")


#-----------------------------------------
def search_web(query):
    return ask_llm(f"Search the web for: {query}")


def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather API key missing."


    try:
        geo = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}").json()
        if not geo: return f"City '{city}' not found."
        lat, lon = geo[0]["lat"], geo[0]["lon"]


        data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric").json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        return f"In {city}: {temp}°C, {desc}, humidity {humidity}%."
    except Exception as e:
        return f"Weather API error: {e}"


def summarize_text(text):
    return ask_llm(f"Summarize this text concisely:\n{text}")


def write_code(instruction):
    return ask_llm(f"Write Python code for: {instruction} without comments.")


#-----------------------------------------
def call_tool(tool, params):
    tool = tool.lower()
    if tool == "calculator": return calculate(**params)
    elif tool in ["search", "search_web"]: return search_web(**params)
    elif tool == "get_weather": return get_weather(**params)
    elif tool == "summarize_text": return summarize_text(**params)
    elif tool == "write_code": return write_code(**params)
    else: return f"Unknown tool: {tool}"


#-----------------------------------------
def extract_final_answer(text):
    if not text:
        return "No response available"

    # Try to get the last number in the response
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    if numbers:
        return numbers[-1]
    return text.strip()  # fallback: return whole response


def scratch_agent(question, max_steps=5):
    history = []
    step = 0


    tools_list = """
calculator (add, subtract, multiply, divide, power, square_root, log, sine, cosine, tangent)
search_web (query)
get_weather (city)
summarize_text (text)
write_code (instruction)

IMPORTANT: Use this EXACT format:
Action: tool_name
Action Input: param1, param2, param3

When you have the final answer, write: Final Answer: [your answer]
"""


    while step < max_steps:
        prompt = f"""
You are a reasoning agent. Solve the question using the available tools.
Tools: {tools_list}
History:
{chr(10).join(history[-5:])}
Question: {question}
Thought:"""


        response = ask_llm(prompt)

        if not response:
            print("LLM returned empty response, stopping agent.")
            return "LLM response error - please try again"


        print(f"LLM Response:\n{response}\n")


        # Check if LLM already gives answer
        if "final answer" in response.lower() or step == max_steps - 1:
            final = extract_final_answer(response)
            print(f"\nFinal Answer: {final}")
            return final


        # Parse tool usage
        if "Action:" in response and "Action Input:" in response:
            try:
                lines = response.split("\n")
                tool_line = None
                input_line = None

                for line in lines:
                    if "Action:" in line and not tool_line:
                        tool_line = line
                    elif "Action Input:" in line and not input_line:
                        input_line = line

                if tool_line and input_line:
                    tool_name = tool_line.split("Action:")[-1].strip()
                    inputs_str = input_line.split("Action Input:")[-1].strip()

                    inputs = [inp.strip().strip('"').strip("'") for inp in inputs_str.split(",")]


                    params = {}
                    tn = tool_name.lower()
                    if tn == "calculator":
                        params["operator"] = inputs[0].strip()
                        params["x"] = float(inputs[1].strip())
                        if len(inputs) > 2: params["y"] = float(inputs[2].strip())
                    elif tn in ["search", "search_web"]:
                        params["query"] = inputs[0].strip()
                    elif tn == "get_weather":
                        params["city"] = inputs[0].strip()
                    elif tn == "summarize_text":
                        params["text"] = inputs[0].strip()
                    elif tn == "write_code":
                        params["instruction"] = inputs[0].strip()


                    observation = call_tool(tool_name, params)
                    history.append(f"{response}\nObservation: {observation}\nThought:")
                    step += 1
                else:
                    print("Could not parse action format")
                    history.append(response)
                    step += 1


            except Exception as e:
                print("Parsing action failed:", e)
                history.append(f"{response}\nError: {e}\nThought:")
                step += 1
        else:
            history.append(response)
            step += 1


    print("Max steps reached without explicit final answer.")
    if history:
        return extract_final_answer(history[-1])
    return "Could not determine final answer"


#-----------------------------------------
if __name__ == "__main__":
    # q1 = "I want to add 2 and 3 then divide by 5."
    # print(f"Q1: {q1}")
    # result = scratch_agent(q1)
    # print(f"Result: {result}\n")
    # print("-" * 50 + "\n")


    # q2 = "Alfred buys an old scooter for Rs. 4700 and spends Rs. 800 on repairs. If he sells the scooter for Rs. 5800, his gain percent is:"
    # print(f"Q2: {q2}")
    # result = scratch_agent(q2)
    # print(f"Result: {result}\n")
    # print("-" * 50 + "\n")


    q3 = "What is the weather in Mumbai? "
    print(f"Q3: {q3}")
    result = scratch_agent(q3)
    print(f"Result: {result}\n")
    print("-" * 50 + "\n")


    # q4 = "Summarize the plot of the movie Inception."
    # print(f"Q4: {q4}")
    # result = scratch_agent(q4)
    # print(f"Result: {result}\n")
    # print("-" * 50 + "\n")


    # q5 = "Write a python function to check if a number is prime."
    # print(f"Q5: {q5}")
    # result = scratch_agent(q5)
    # print(f"Result: {result}\n")
