import openai

openai.api_key = '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'

def analyze_emotion(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    generated_text = response.choices[0].text.strip()
    return generated_text


