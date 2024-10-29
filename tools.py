import requests

def get_crypto_price(crypto_name):
    if not crypto_name:
        return "No information found"
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': crypto_name.lower(),
        'vs_currencies': 'inr'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if crypto_name.lower() in data:
            price = data[crypto_name.lower()]['inr']
            return f"The current price of {crypto_name} is {price} INR"
        else:
            return f"Cryptocurrency '{crypto_name}' not found."
    
    except:
        return "Could not fetch the price."


tools = [
  {
    "type": "function",
    "function": {
      "name": "get_crypto_price",
      "description": "Fetch the current price of a specified cryptocurrency",
      "parameters": {
        "type": "object",
        "properties": {
            "crypto_name": {
                "type": "string",
                "description": "Name of the cryptocurrency",
            },
        },
        "required": ["crypto_name"],
    },
    }
  }
]

