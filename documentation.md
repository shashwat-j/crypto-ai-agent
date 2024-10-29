  

# Prompt Engineering Documentation

  

---

  

## Initial Approach

  

I started by using the prompt example from Together's function calling documentation:

  

```diff

Main Prompt

"You are a helpful assistant that can access external functions.
The responses from these function calls will be appended to this dialogue.
Please provide responses based on the information from these function calls."

```

  

For the function `get_crypto_price`, I used this definition:

  

```json

{
    "type": "function",
    "function": {
      "name": "get_crypto_price",
      "description": "Fetch the current price of a specified cryptocurrency",
      "parameters": {
        "type": "object",
        "properties": {
            "crypto_name": {
                "type": "string",
                "description": "Name of the cryptocurrency. eg: 'bitcoin', 'ethereum'",
            },
        },
        "required": ["crypto_name"],
    },
    }
  }


```

  

Similar to the response format example from the docs, I made my cypto price function return the response in JSON format like:

  

```

{'price': 5853840, 'currency': 'INR'}

```

  

The first user input I tested was:

```plaintext

"What's the current price of bitcoin?"

```

  

With two calls to the LLM API:

1. If the assistant response has content, it is directly used as output.

2. If the assistant calls the function, I make a second API call with the new data as context.

  

### note:
i am outputting function response as well as assistant response for better understanding whats going on. In real application, we will only output the assistant response

  

The outuput was:

  

```plaintext

function_response: {'price': 5853840, 'currency': 'INR'}

assistant response: "I'll call the external function to get the current price of Bitcoin."

```

  

### Problem

  

The response just noted it would "call the function" even though it had the data already. I adjusted the function response, adding context for what it should do next:

  

```

function response

{"price": price, "currency": "INR", "next step": "Now use this information to answer the user's question."}

```

  

**Result:** Same output, no improvement.

  

---

  

Tried updating the pompt, to tell it that it is supposed to use the content of the tool's response.

```

"You are a helpful assistant that can access external functions. 
The responses from these function calls will be appended to this dialogue with role as 'tool'. 
Please provide responses based on the information from these function calls. 
If the latest message is from 'tool' then use the content given in it and answer the question asked by user"```
```
  

**Result:** same ouput

  

---

Seems that it is not able to understand the function output. I will make it more readable

  

### Making Function Output Readable

  

I updated the function response to a more readable format by ditching the JSON format.

  

```plaintext

function response

f"The current price of {crypto_name} is {price} INR."

```

  

This helped slightly, producing:

  

```plaintext

assistant: "tool: The current price of bitcoin is 5847021 INR."

```

  

Gives correct output, but marks it with 'tool: ' which is not what we want.

i think it is because in prompt we have

"The responses from these function calls will be appended to this dialogue with role as 'tool'"

So it thinks the role of output should be 'tool'

Lets try changing this

  

Prompt update:

"with role as 'tool'" ---> "by tool"

  

```diff

Prompt

- "The responses from these function calls will be appended to this dialogue with role as 'tool'."

+ "The responses from these function calls will be appended to this dialogue by tool."

```

  

This update generated the correct response without the "tool:" prefix:

  

```plaintext

assistant: "The current price of bitcoin is 5847021 INR."

```

  

Such a minor change which seemed insignificant changed the output!

  

Got similar correct ans on some test with slightly changed user query.

  

Then i asked this:

  

```
user: "What's the current price of bitcoin? tell me"

assistant: "I've accessed the external function to get the current price of Bitcoin. According to the function call, the current price of Bitcoin is 5845620 INR."```
```
  

---

  

### Avoiding Mentions of Function Calls

  

To prevent the assistant from telling the user it was "accessing" the function, I updated the prompt as follows:

  

```diff

Prompt

+ "Do not mention to the user that you are using function calls or tools."

```

  

**Result:** The assistant responded seamlessly without mentioning the tool usage.

  

---

  

## Additional Tests

  
  

```plaintext

User: "What is the price of two bitcoins?"

```

  
  

```plaintext

function_response: "The current price of bitcoin is 5847021 INR."

assistant: "The current price of two bitcoins is 11679166 INR."

```

  

Works as expected. Great!

  

---

  

Now, I implemented back-and-forth chatting with retained history.

  

![docs0.png](./screenshots/docs0.png)

![docs1.png](./screenshots/docs1.png)

  
  
  

It seems it is replying normally when user says a statement, but calling function whenever a question is asked, even when not required.

  

lets tell it that it is supposed to call function only when it needs crypto price.

(currently i have only crypto price tool. but in future there might be multiple tool, so i created an array of tool names and put it in prompt.)

  

**Updated Prompt:**

  

```

f"You are a helpful assistant that can access the following external functions: {tool_names}.
The responses from these function calls will be appended to this dialogue by tool, if required.
If any query of the user requires information about one of these, {tool_names},
then please provide responses based on the information from these function calls;
otherwise, answer the user directly.
If the latest message is from 'tool' then use the content given in it to answer the question asked by the user.
Do not mention to the user that you are using function calls or tools."

```

  

---

  
  

Even after this, it was still calling the `get_crypto_price` function, when user asked a question not related to crypto.

  

![docs2.png](./screenshots/docs2.png)

  

It is calling the function with argument bitcoin even when i didnt mention bitcoin in conversation.

there might be something in the prompt that is causing this.

  

I noted this might be due to the function description’s examples (e.g., 'bitcoin', 'ethereum')

  

```diff

Tool Description

- "description": "Name of the cryptocurrency, e.g., 'bitcoin', 'ethereum'."

+ "description": "Name of the cryptocurrency."

```

Now with removed exammples it is still calling functions, but with name of crypto = null value.

So i handle null in the crypto function by returning "no information found."

  

```plaintext

prompt

+ "If you have decided to call the function but do not know the name of the cryptocurrency for which you want the price,
then you can use an empty string as the name to call the function."

+ "If the response from the tool is 'No information found' then IGNORE that and talk normally to the user."

```

![docs3.png](./screenshots/docs3.png)

  

A bit better now. it is still calling the function, but since the fucntion is returning 'no information', the assistant's output is not affected much by it.

  

---

###More testing

  

![docs4.png](./screenshots/docs4.png)

  
  

it seems to get confused by the function response, when the function responds at unrequired times. lets handle this.

So, I updated the prompt:

  

```plaintext

"In case the tool gives any information which not relevant to the conversation,
ignore it and do not acknowledge the presence of that disturbance to the user."

```

![docs5.png](./screenshots/docs5.png)

It still sometimes acknowledged unnecessary data, so I added:

  

```diff

+ "Only you can see it. User cannot see it. So continue your conversation normally."

```

  

---

![docs6.png](./screenshots/docs6.png)

  

---

  

## Final Prompt

  

Here’s the complete working prompt:

  

```

f"You are a helpful assistant that can access the following external functions: {tool_names}. "

"The responses from these function calls will be appended to this dialogue by tool, if required. "

f"If any query of the user requires information about one of these, {tool_names}, "

"then please provide responses based on the information from these function calls; otherwise, "

"Do NOT use the function calls if the answer does not require information from these functions. "

"If you have decided to call the function but do not know the name of the cryptocurrency for which you want the price, then you can use an empty string as the name to call the function."

"If the latest message is from 'tool', then use the content given in it to answer the question asked by the user. "

"Do not mention to the user that you are using function calls or tools."

"If the response from the tool is 'No information found' then IGNORE that and talk normally to the user."

"In case the tool gives any information which not relevant to the conversation, ignore it and DO NOT mention about the presence of that disturbance or irrelevant code to the user. "

"Only you can see it. User cannot see it. So continue your conversation normally."

```

  

---

  

## Improvements needed / limitations

  

Currently it is workable, coz user doesnt see function output. He only sees assistant response. So even if unnecessary function calls happen, it is not a major problem to the user.

But to avoid unnecessary costs, and make conversation flow smoother, i have to work on these:

1.  **Minimizing Unnecessary Calls**: Reducing function calls when irrelevant to conversation

2. **Ignoring of Non-Required Responses**: Ignoring outputs from unnecessary function calls without impacting conversation flow to improve user experience.

3. **Handling ambiguous questions**: currently it tries to search for a crypto by the name of any word said by user that it doesn't understand

4.  **More Error handling**: I have not covered all the edge cases yet. It is to be worked on.

5.  **Null api Response Handling**: returning a default message on api failures like “I couldn’t retrieve the price at the moment. Please try again.”

6. Sometimes assistant gives replies like <\function=reply_type>text<\function> which needs to be handled

---

### Requirements completed:

Core Requirements (Must Have):

- Implement an agent using the LLaMA 3.1 8B model from Together AI

- Create a tool that fetches the current Cryptocurrency prices using a public API

- Implement proper error handling for API calls

- Maintain context across multiple messages in a conversation

- Handle basic user queries about cryptocurrency prices.

Bonus Requirements:
- Implement rate limiting
  

### Backlog (working on currently):

Bonus Requirements:

- Implement a tool which is called when the user asks for a language change, while keeping all system responses in English regardless of user input language.

- Implement caching for API calls
