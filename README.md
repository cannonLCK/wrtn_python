# wrtn_python
Wrtn.ai reverse proxy
with an unofficial openai-style api: 8k token GPT4 with full support of an openai-style json format.  

Also works well with Sillytavern.

# usage
localhost:41232

# You need a file named 'wrtn.json' contains
```
[
    {
        "id": "name@example.com",
        "pw": "example_password",
        "key": "eyJhXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.eyJXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        //refresh key
    },
```
If you don't know how to get the refresh_key, don't worry, as long as you input the id and pw correctly, it will automatically update the refresh_key.

