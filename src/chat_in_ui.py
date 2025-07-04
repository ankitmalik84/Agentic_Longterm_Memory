import time
import gradio as gr
from utils.basic_chatbot_v1 import Chatbot
from utils.chatbot_agentic_v2 import Chatbot as Chatbot_v2
from utils.chatbot_agentic_v3 import Chatbot as Chatbot_v3

# Initialize chatbot instances
chatbots = {
    "Basic-Chatbot": Chatbot(),
    "Chatbot-Agentic-v2": Chatbot_v2(),
    "Chatbot-Agentic-v3": Chatbot_v3(),
}


def respond(selected_bot, history, user_input):
    if not user_input.strip():
        return history, ""

    chatbot = chatbots[selected_bot]
    start_time = time.time()
    response = chatbot.chat(user_input)
    end_time = time.time()

    # Append user and assistant responses to the history
    history.append(
        (user_input, f"{response} ({round(end_time - start_time, 2)}s)"))
    return history, ""


with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("Chatbot with Agentic Memory"):
            with gr.Row():
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    height=500,
                    avatar_images=("images/AI_RT.png", "images/openai.png"),
                )

            with gr.Row():
                input_txt = gr.Textbox(
                    lines=3,
                    scale=8,
                    placeholder="Enter text and press enter...",
                    container=False,
                )

            with gr.Row():
                text_submit_btn = gr.Button(value="Submit")
                clear_button = gr.ClearButton([input_txt, chatbot])
                selected_bot = gr.Dropdown(
                    choices=["Basic-Chatbot", "Chatbot-Agentic-v2",
                             "Chatbot-Agentic-v3"],
                    value="Chatbot-Agentic-v3",
                    label="Select Chatbot Version"
                )

            # Handle submission
            input_txt.submit(
                fn=respond,
                inputs=[selected_bot, chatbot, input_txt],
                outputs=[chatbot, input_txt]
            )

            text_submit_btn.click(
                fn=respond,
                inputs=[selected_bot, chatbot, input_txt],
                outputs=[chatbot, input_txt]
            )

if __name__ == "__main__":
    demo.launch()
