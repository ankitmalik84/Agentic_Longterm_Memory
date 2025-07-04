import time
from utils.basic_chatbot_v1 import Chatbot
from utils.chatbot_agentic_v2 import Chatbot as Chatbot_v2
from utils.chatbot_agentic_v3 import Chatbot as Chatbot_v3

# If you'd like to chat with a different chatbot, modify the code manually.
# chatbot_version = "basic"
# chatbot_version = "v2"
chatbot_version = "v3"

if __name__ == "__main__":
    if chatbot_version == "basic":
        print("Basic chatbot is initialized. Type 'exit' to end the conversation.")
        chatbot = Chatbot()
    elif chatbot_version == "v2":
        print("Chatbot-agentic-v2 is initialized.  Type 'exit' to end the conversation.")
        chatbot = Chatbot_v2()
    elif chatbot_version == "v3":
        print("Chatbot-agentic-v3 is initialized.  Type 'exit' to end the conversation.")
        chatbot = Chatbot_v3()

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Get response from the chatbot
        print("\nThinking...")
        start_time = time.time()
        response = chatbot.chat(user_input)
        end_time = time.time()

        print(f"\nAssistant ({round(end_time - start_time, 2)}s): {response}")
