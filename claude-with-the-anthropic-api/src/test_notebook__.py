
## /home/dhankar/temp/26_04/claude_certs/test_notebook__.py
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

# Make a request
def chat(messages):
    """ 
    """
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content":  "hello- whats the sum of -- 6677 + 8899 "
            }
            
        ]
    )

    print(message)
    print(message.content[0].text)

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


"""