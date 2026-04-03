
## /home/dhankar/temp/26_04/claude_certs/test_notebook__.py
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"

ls_messages = []

def add_user_message(ls_messages, text):
    user_message = {"role": "user", "content": text}
    ls_messages.append(user_message)

def add_assistant_message(ls_messages, text):
    assistant_message = {"role": "assistant", "content": text}
    ls_messages.append(assistant_message)


def chat(ls_messages):
    """ 
    """
    print("---FROM--CHAT-----print(type(ls_messages))-------")
    print(type(ls_messages))
    print("  -- "*100)

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=ls_messages
    )

    print("---FROM--CHAT------------")
    print(message)
    print("  "*100)
    print(message.content[0].text)
    print("  "*100)
    return message


new_message_text = "Hello whats the sum of -- 667700 + 448899 "
add_user_message(ls_messages,new_message_text)

answer = chat(ls_messages)
print("---FROM--module---answer--------")
print(answer)
print("  "*100)
print("---FROM--module---type(answer))--------")
print(type(answer)) ## <class 'anthropic.types.message.Message'>
print("  "*100)
print("---FROM--module---type(answer))--------")
answer_text = answer.content[0].text
print(type(answer_text))
print("  "*100)

add_assistant_message(ls_messages,answer_text) #answer.content[0].text


# Add another New random sentence
new_message_text_random = "Add another sentence "
add_user_message(ls_messages,new_message_text_random)

#Answer 2 Now 
answer_2 = chat(ls_messages)
print("---FROM--module---answer_2--------")
print(answer_2)
print("  "*100)



""" 
python test_notebook__.py 

Message(id='msg_014pGjCMaKi75J9aDAXUUWJa', container=None, content=[TextBlock(citations=None, 
text='Hello! Let me calculate that for you:\n\n6677 + 8899 = 15,576\n\nThe sum is 15,576.', 
type='text')], model='claude-sonnet-4-20250514', 
role='assistant', 
stop_reason='end_turn', 
stop_sequence=None, 
type='message', 
usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), 
cache_creation_input_tokens=0, 
cache_read_input_tokens=0, 
inference_geo='not_available', 
input_tokens=24, 
output_tokens=35, 
server_tool_use=None, 
service_tier='standard'), stop_details=None)

(env_overlander) dhankar@dhankar-1:~/.../claude_certs$ 

[
            {
                "role": "user",
                "content":  "hello- whats the sum of -- 6677 + 8899 "
            }
            
        ]


"""