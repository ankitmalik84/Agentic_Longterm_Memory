# 🧠 Agentic Chatbot v2

This version of the chatbot transforms the assistant into an **interactive agent** that can **call tools**, retrieve information, and update user data, all using OpenAI's function calling system.

This is where we start to introduce **agentic behavior** and **custom function execution** into the flow.

## 🔍 Core Functionalities

### 🔧 1. **System Initialization**

Similar to the Basic Chatbot, when the chatbot starts, it sets up:
- **OpenAI Client** – to talk to the GPT model.
- **UserManager & ChatHistoryManager** – to track who's talking and store what's been said and adding the long-term memory to our system.
- **Configuration** – loads temperature, max tokens, model name, etc.

But this version **adds new capabilities**, including:

- `Utils`: Converts Python functions into OpenAI-compatible JSON schemas
- `SearchManager`: Allows the chatbot to query the SQL database using **keyword or phrase-based search**
- `agent_functions`: A list of callable tools for the agent, including:
  - `add_user_info_to_database`
  - `search_chat_history`

> Think of this as preparing the brain, memory, and tools for the conversation.

---

### 💬 2. **Conversation Flow**

Each user message follows a **loop** that looks like this:

1. **User sends a message**  
2. **Chatbot builds a prompt**:
   - Includes:
     - User info
     - Current user message
     - Recent chat history
     - A summary of earlier conversations
     - Any previous function results (if any)

3. **Prompt sent to GPT with special powers**:
   - The model can **either reply directly** or
   - **Request to call a function** (like "search_chat_history" or "add_user_info_to_database")

4. **If a function is requested**:
   - The chatbot **executes the function**
   - **Saves the result**
   - Builds a new system prompt including the result
   - **Loops back** to GPT for a final response

5. **If there's no function or after executing one**, the chatbot:
   - **Stores the conversation** in a local database
   - **Updates the summary**
   - Sends the final response to the user

---

### ⚙️ 3. **Function Execution Mechanism**

The chatbot supports **JSON-based function calling**, where GPT decides *what tool to use* and *what arguments to provide*:

For example:
- GPT might say:  
  “Call `add_user_info_to_database` with this info: `name=John, age=32`”
- The chatbot executes that function
- Returns the success/failure result back to GPT
- GPT continues the conversation with updated context

---

### 📦 4. **Components Overview**

| Component | Purpose |
|----------|---------|
| `UserManager` | Tracks user data, saves it to DB |
| `ChatHistoryManager` | Manages the long-term memory |
| `SearchManager` | Allows GPT to search previous chats |
| `Utils` | Helps format function schemas |
| `prepare_system_prompt` | Builds the "brain state" prompt for GPT |
| `Config` | Handles settings like model, temperature, etc. |

---

### 🔁 5. **Failsafe Mechanism**

If GPT requests **too many functions** (e.g., in a loop), or **fails**, a fallback mechanism triggers:
- GPT is called again without function access
- Generates a direct response from available context


## 🔄 Key Differences vs. Basic Chatbot

| Feature | **Basic Chatbot** | **Agentic Chatbot v2** |
|--------|-------------------|-------------------------|
| **Chat Flow** | One-step response | Multi-step agentic loop |
| **Function Calling** | ❌ None | ✅ OpenAI tools supported |
| **Abilities** | Only responds | Updates DB, searches, adapts |
| **Search Capability** | ❌ None | ✅ Phrase-based SQL search |
| **Prompt Strategy** | Simple prompt | Prompt with call context |
| **Fallback Strategy** | ❌ None | ✅ Includes a fallback mechanism|
| **Memory Handling** | Short-term only | Tracks function call memory |

---

## 🧾 Architecture Overview

Here's the architecture of Agentic Chatbot v2:

![Agentic Chatbot v2 Schema](../images/chatbot_agentic_v2.png)
