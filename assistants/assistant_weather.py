import json
import requests

def createFunctions_weather():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Determine weather in my location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["c","f"]
                        }
                    },
                    "required": [
                        "location"
                    ]
                }
            }
        }
    ]

locationcache = [
    {"name": "london", "lat": 51.51415, "long": -0.11473},
    {"name": "budapest", "lat": 47.49608, "long": 19.06288}
]

def initModule(client, assistant):
    return

def handleToolCall(function_name, arguments, client=None):
    #print('weather tool')
      # only one function in this example, but you can have multiple

    if(function_name in available_weather_functions):
        function_to_call =  available_weather_functions[function_name]
        function_args = json.loads(arguments)
        function_response = function_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit", "c"),
        )
        if function_response is not None:
            return json.dumps(function_response)
    
    return None

def get_coordinates(location):
    print("Determining location coordinates with geocode API... " + location)

    for loc in locationcache:
        if loc["name"].lower() == location.lower():
            print("Found location in cache")
            return loc["lat"], loc["long"]
        
    geocode_response = requests.get(f'https://geocode.xyz/{location}?json=1')
    geocode_data = geocode_response.json()
    
    if "error" in geocode_data:
        raise ValueError("Invalid location")
    
    latitude = geocode_data.get('latt')
    longitude = geocode_data.get('longt')
    print("lat: " + latitude + " long: " + longitude)

    return latitude, longitude
    

def get_weather(location, unit="c"):
    try:
        latitude, longitude = get_coordinates(location)

        # Step 2: Fetch weather data using Open-Meteo API with the obtained coordinates
        print("Fetching weather data using Open-Meteo API...")
        response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true')
        #print(response)
        data = response.json()

        if 'current_weather' in data:
            temperature_celsius = data['current_weather']['temperature']
            temperature = (temperature_celsius * 9/5) + 32 if unit == "f" else temperature_celsius
            return {
                "location": location,
                "temperature": f"{temperature:.1f}°{unit.upper()}",
                "unit": unit,
                "current_weather": data['current_weather']
            }
        else:
            return {"error": "Weather data not available"}

    except Exception as e:
        return {"error": str(e)}


available_weather_functions = {
        "get_current_weather": get_weather,
    }