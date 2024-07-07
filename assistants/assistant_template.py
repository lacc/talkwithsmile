
import json
def createFunctions_template():
    return []

def handleToolCall(function_name, arguments):
    #print('weather tool')
      # only one function in this example, but you can have multiple

    if(function_name in available_weather_functions):
        function_to_call =  available_weather_functions[function_name]
        function_args = json.loads(arguments)
        function_response = function_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit", "c"),
        )

        return json.dumps(function_response)
    
    return False

available_weather_functions = {
        "get_current_weather": get_weather,
    }

def get_weather(location, unit="c"):
    return {}
