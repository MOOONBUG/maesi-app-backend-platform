import os
from openai import OpenAI

# 请在这里填入你真实的中转站 Key 和真实的中转站地址（确保 base_url 包含 /v1）
client = OpenAI(
    api_key="sk-tI2EfT3kDSQRHSEu0zV7nQgAbuzjquxuxAjwSUDofyLk8ZQO", 
    base_url="https://torchai.ai/v1"
)

try:
    print("Connecting to LLM...")
    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.1
    )
    print("Success! LLM Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("Failed with error:", str(e))