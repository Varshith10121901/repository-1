from  openai import OpenAI

client = OpenAI(
    base_url="https://beta.sree.shop/v1",
    api_key="ddc-beta-xd2gpihwcy-FdWG1A2INYMVXbWR8TBmUEx74I3dBRnjwK2"  # Replace with your beta API key
)

response = client.chat.completions.create(
    model="DeepSeek-R1",  # Beta model
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)