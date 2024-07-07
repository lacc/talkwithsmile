from openai import OpenAI
from assistants import assistant_weather
from assistants.assistant_todaymenu import today_menu_assistant  
import json
from datetime import datetime

gptmodel="gpt-4-turbo"
#gtpmodel="gpt-3.5-turbo"

client = OpenAI(
)
messages = [{
    "role": "system",
    "content": "You are the asistant for the hotel HotelExp in London and you are assisting guests with ther needs. You are a kiosk in the hotel reception. You will talk with the guests. You will solve their problems, answer questinos, and give recomendations with upsale opportunities. Do not repeat yourself. You can use similar speaking style like the guest who you are talking to, but keep it still polite and professional."
}]

function_tools = [
    {
        "functiondef": assistant_weather,
        "tools": assistant_weather.createFunctions_weather()
    },
    {
        "functiondef": today_menu_assistant,
        "tools": today_menu_assistant.createFunctions_todaymenu(client)
    }
]

def clear_session():
    messages = []


def handle_prompt(prompt, max_tokens=150):
    prompt = "Current date time: " + str(datetime.now()) + "\n"  + prompt
    messages.append({
            "role": "user", 
            "content": prompt
        })
        
    all_tools = [tool for function_tool in function_tools for tool in function_tool["tools"]]

    response = client.chat.completions.create(
        model=gptmodel,
        messages=messages,
        tools=all_tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        max_tokens=max_tokens 
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    #tool_calls = response_message.get("tool_calls", [])
    #print(response.choices[0].finish_reason)

    if tool_calls:
          
        messages.append(response_message)
        for tool_call in tool_calls:
            #print("tool_call name: " + tool_call.name)

            for function_tool in function_tools:
                function_to_call = function_tool["functiondef"]
                if tool_call.function:
                    
                    function_name = tool_call.function.name
                    print("calling function: " + function_name)

                    function_response = function_to_call.handleToolCall(function_name, tool_call.function.arguments, client)
                    #print(function_response)
                    if function_response is not None:
                        function_response_dict = json.loads(function_response)
                        content = function_response_dict.get("content", function_response)
                        attachments = function_response_dict.get("attachments", [])
                        #print(content)

                        if attachments:
                            tool_response = {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": content,
                                "attachments": attachments,
                            }
                            messages.append(tool_response)
                        else:
                            tool_response = {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content":  content
                            }
                            messages.append(tool_response)
              
        second_response = client.chat.completions.create(
            model=gptmodel,
            messages=messages,
            max_tokens=max_tokens
        )  
        
        messages.append(second_response.choices[0].message)

        return second_response.choices[0].message.content

    return response_message.content

def conert_to_audio(text, file):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    response.stream_to_file(file)

    # Generate speech response and save to a temporary file
    #tts = gTTS(text=text, lang='en')
    #tts.save("response.mp3")
