from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools import tool
import requests

@tool("get_products", description="Get the products that the store offers and their prices. Requires 'price' (int): maximum price to filter products.")
def get_products(price: int):
    """
    Get the products that the store offers and their prices, filtering by a maximum price.
    Args:
        price (int): Maximum price to filter products.
    """
    response = requests.get("https://api.escuelajs.co/api/v1/products")
    products = response.json()
    return "".join([f"{product['title']}: ${product['price']}\n" for product in products if product["price"] <= price])

@tool("get_weather", description="Get weather for a city")
def get_weather(city: str) -> str:
    response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
    data = response.json()
    latitude = data["results"][0]["latitude"]
    longitude = data["results"][0]["longitude"]
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true")
    data = response.json()
    response = f"The weather in {city} is {data['current_weather']['temperature']} C with {data['current_weather']['windspeed']} km/h of speed "
    return response

tools = [get_products, get_weather]


system_prompt = """\
Eres un asistente de ventas que ayuda a los clientes a encontrar los productos que necesitan y también les puedes dar el clima actual de su ciudad.

Tus Tools son:
- get_products(price: int): Get the products that the store offers and their prices, filtering by a maximum price.
- get_weather(city: str): Get the current weather for a given city.
"""

llm = ChatOllama(model="qwen2.5:7b", temperature=0)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)