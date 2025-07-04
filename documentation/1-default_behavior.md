

# Why LLMs Don't Have Memory by Default

Large Language Models (LLMs) like GPT are incredibly powerful at generating human-like text.  
However, **they do not have memory by default**, which means:

- They **do not remember previous interactions** across different sessions.
- They **cannot persist knowledge** about users, past conversations, or ongoing tasks beyond the current input context.


## 🧠 What "No Memory" Really Means

Unlike humans or stateful systems, LLMs are:

- **Stateless**: Every prompt is treated as a brand new request, with no awareness of previous conversations.
- **Context-limited**: They only "see" what's in the current prompt.

---

## 📦 How LLMs Process Input

![Schema of Stateless LLM Input and Output](../images/default_behavior.png)

This is how LLMs work without memory:

1. The user sends a prompt.
2. The LLM generates a response based only on the text provided.
3. Once the response is returned, the model **forgets everything** — it does not retain any data from the interaction.

Unless memory is engineered on top, this cycle repeats every time.

---

## ⚠️ Why This Matters

Without memory:
- The user must constantly repeat context.
- The LLM can't build a personalized relationship or learn user preferences.
- Multi-step tasks become harder to complete.
- Emotional, historical, or task continuity is lost between interactions.

---

## 🛠️ Workarounds

To overcome this limitation, we can design memory architectures **around** the LLM. These are some of the strategies used:

- **Storing chat history in databases** (SQL, VectorDBs, GraphDBs, etc.)
- **Using vector stores** for semantic memory retrieval (e.g., remembering topics or sentiments)
- **Graph databases** to model structured relationships, user profiles, interests, and more
- **Summarizing long interactions** to fit more context into the limited prompt size
- **Building agentic loops** that use tools and store relevant knowledge over time to guide behavior


- **Designing more powerful LLMs:** means creating models that can understand and process longer inputs.
---

> ⚡ **Bottom line:**  
> LLMs are powerful but forgetful.  
> Memory must be engineered externally to unlock their full potential.

---

## 🧠 Why Don't We Just Design LLMs with Infinite Context Length?

LLMs like GPT are based on the transformer architecture, which has a key limitation: the attention mechanism. This mechanism compares every word (or token) in the input with every other word, which results in quadratic growth in computation and memory. Specifically, if you double the input length, the computation doesn't just double—it grows four times.

For example, processing 1,000 tokens may take a certain amount of time and memory, but processing 10,000 tokens takes 100 times ((10,000² / 1,000²) = 100) more resources. This makes it very expensive and slow for models to handle very long texts.

Moreover, storing all the information from long sequences becomes difficult due to hardware limits (like GPU memory). This is why LLMs can't have infinite context length. Researchers are working on ways to improve this, like using sparse attention or memory-augmented models, but it's still an ongoing challenge.

In the standard self-attention mechanism, the computational cost scales with the square of the sequence length (O(n²), where n is the number of tokens). This is because each token attends to every other token, resulting in n × n comparisons. If you double the input length (e.g., from n to 2n), the computation increases by a factor of four (2n × 2n = 4n²), not just two.

---