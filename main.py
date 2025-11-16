from settings import settings
from openai import OpenAI



def main():

    client = OpenAI(
        base_url=settings.litellm_url,
        api_key=settings.api_key,
    )

    # First API call with reasoning
    response = client.chat.completions.create(
      model=settings.model_name,
      messages=[
              {
                "role": "user",
                "content": "How many r's are in the word 'strawberry'?"
              }
            ],
      extra_body={"reasoning": {"enabled": True}}
    )

    # Extract the assistant message with reasoning_details
    print(response.choices[0].message) 


if __name__ == "__main__":
    main()
