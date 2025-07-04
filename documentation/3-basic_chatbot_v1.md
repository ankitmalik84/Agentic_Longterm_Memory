# 🤖 Basic Chatbot

This is the simplest form of a memory-aware chatbot.  
It uses OpenAI's chat models combined with persistent history management to enable short-term context retention across turns.

The goal of this chatbot is to create a conversational loop that remembers **recent history**, personalizes replies based on **user info**, and summarizes past interactions, without advanced memory systems.

## ⚙️ Core Functionalities

### 1. 🧱 Initialization

When the `Chatbot` class is initialized, it sets up:

- ✅ **Model Configuration**  
  Loads model names, token limits, and paths from a configuration file.

- ✅ **Session ID Generation**  
  Each chat session is assigned a unique ID for tracking.

- ✅ **Components Setup**
  - `SQLManager`: Connects to a local or remote database
  - `UserManager`: Retrieves or stores user information
  - `ChatHistoryManager`: Tracks message history and summaries

- ✅ **Chat Summary Retrieval**  
  Pulls the most recent conversation summary to preserve continuity in new prompts.

---

### 2. 💬 Conversational Handling

When a message is received:

- 📌 **System Prompt Construction**  
  Dynamically builds a prompt including:
  - User profile details
  - A summary of earlier chats
  - The last few message pairs

- 🔁 **Model Invocation**  
  Sends the prompt and user message to OpenAI's API and receives a reply.

- 🧠 **Chat History Update**
  - Stores the conversation pair in the database
  - Updates the summary if needed to stay within context length

- ⚠️ **Error Handling**  
  Any issues during the API request return a readable error message.

---

## 🧾 Visual Overview

Here's a high-level schema showing how the basic chatbot works:

![Basic Chatbot Architecture](../images/basic_chatbot.png)

---

> 🧩 This chatbot doesn't support tool usage or long-term memory.  
> But it's a solid foundation for building more advanced, agentic systems.
