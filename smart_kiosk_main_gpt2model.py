import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained GPT-2 model and tokenizer
print("Loading tokenizer...")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
print("Loading model...")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Function to generate response based on user input
def generate_response(input_text, max_length=100):
    # Tokenize input text
    print("Tokenizing input text...")
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    print("Input IDs:", input_ids)

    # Generate response
    output = model.generate(input_ids, max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return generated_text

# Main function to interact with the user
def main():
    print("Welcome to Smart Hotel Kiosk!")
    print("Type 'exit' to end the conversation.")
    
    while True:
        # Get user input
        user_input = input("You: ")

        # Check for exit command
        if user_input.lower() == 'exit':
            print("Exiting...")
            break

        # Generate response
        response = generate_response(user_input)
        print("Kiosk:", response)

if __name__ == "__main__":
    print("Start main...")
    main()
