from agent import generate_agent_response

def terminal_chat():
    print("Started chat. Type '0' to exit the chat.")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "0":
            break
        success = generate_agent_response(user_input)
    
        if not success:
            print("Exiting due to error.")
            break


terminal_chat()
