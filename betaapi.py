from openai import OpenAI

api_key="ddc-beta-xd2gpihwcy-FdWG1A2INYMVXbWR8TBmUEx74I3dBRnjwK2"

client = OpenAI(
    base_url="https://beta.sree.shop/v1",
    api_key=api_key
)

# print("--- Listing All Models ---\n")
# try:
#     models = client.models.list().data
#     for model in models:
#         print(model.id)
# except Exception as e:
#     print("Error listing models:", e)

print("Normal Chat Completions:")
completion = client.chat.completions.create(
  model="deepseek-v3",
  messages=[
    {"role": "user", "content": "How are you Doing’?"}
  ]
)

print(completion.choices[0].message)

print("\nStream Chat Completions:")
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Congratulations !!!! Hope Your Day is GOOD!!"}
    ],
    stream=True
)

for chunk in completion:
    print(chunk.choices[0].delta.content, end="", flush=True)