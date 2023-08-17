# Wrtn_python
Wrtn.ai python reverse proxy
with an unofficial openai-style api: 8k token GPT4 with full support of an openai-style json format.  

Also works well with Sillytavern.

# Requirement

[fake_useragent](https://pypi.org/project/fake-useragent/)

# Usage
Sillytavern
1. Use localhost:41323 for alternative server URL
2. Turn the streaming mode on

Other
post localhost:41323 with payload format:
```
{
    'messages': [
        {'role': 'system', 'content': 'system prompt'},
        {'role': 'assistant', 'content': "assistant prompt'},
        {'role': 'user', 'content': 'user prompt'}
    ],
    'model': 'gpt-4',
}
```

# Caution
You can't adjust parameters like Temperature, Frequency, Presense penalty, Top-P.
Adjust context sizes and max response length fit with 8k tokens.

# You need a file named 'wrtn.json' contains
```
[
    {
        "id": "name@example.com",
        "pw": "example_password",
        "key": "eyJhXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.eyJXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        //refresh key
    },
    ...
]
```
If you don't know how to get the refresh_key, don't worry, as long as you input the id and pw correctly, it will automatically update the refresh_key.

