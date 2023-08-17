'''
main.py
Reverse proxy for wrtn
support system messages.
'''
from os import path
import time
import json
import wrtn
import random
from aiohttp import web

Wrtn = wrtn.WrtnAPI(debug=False)

from os import path
json_path = path.join(path.dirname(__file__), "./wrtn.json")

async def handle_request(request):
    '''login and retrieve refresh_token, and update json'''
    with open(json_path, "r", encoding='utf-8') as file:
        json_data = json.load(file)
    random_account = random.choice(json_data)
    random_account['key'] = await Wrtn.login(random_account)
    # Write the updated JSON data back to the file
    
    with open(json_path, "w", encoding='utf-8') as file:
        json.dump(json_data, file, indent=4)

    model = lambda id : {"id": id, "object": "model", "created": int(time.time() * 1000), 
                               "owned_by": "", "permission": [], "root": "", "parent": None}
    if request.method != 'POST':
        data = {
            "object": "list",
            "data": [
                model("gpt-3.5-turbo"),
                model("gpt-4"),
            ]
        }
        return web.json_response(data)
    else:
        data = await request.json()
        preprompt = [
            "[Use proper language regarding on a context.]" # No use for forcing a specific language now.
        ]
        system = {
            "role":"system",
            "content": ""
        }
        system['content'] += ' '.join(preprompt)
        oldmsg = [system] + data['messages'][:-1]
        msg = data['messages'][-1]['content']
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'application/json'
        await response.prepare(request)
        temp_res_text = ""
        try:
            chunk = {
                        "id": f"chatcmpl-{(str(random.random())[2:])}", 
                        "created": int(time.time() * 1000), 
                        "object": "chat.completion.chunk", 
                        "model": data["model"], 
                        "choices": [{ "delta": {"role": "assistant"}, "finish_reason": None, "index": 0 }]
                    }
            await response.write(f"data: {json.dumps(chunk)}\n\n".encode())
            async for res_text in Wrtn.chat_by_json(await Wrtn.make_chatbot(),
                msg=msg,
                oldmsg=oldmsg,
                model=data['model']
            ):
                temp_res_text = res_text
                chunk = {
                        "id": f"chatcmpl-{(str(random.random())[2:])}", 
                        "created": int(time.time() * 1000), 
                        "object": "chat.completion.chunk", 
                        "model": data["model"], 
                        "choices": [{ "delta": {"content": res_text}, "finish_reason": None, "index": 0 }]
                    }
                await response.write(f"data: {json.dumps(chunk)}\n\n".encode())
        except Exception as ex:
            print(f"Error: {str(ex)}\n Chunk: {temp_res_text}")
        finally:
            chunk = {
                        "id": f"chatcmpl-{(str(random.random())[2:])}", 
                        "created": int(time.time() * 1000), 
                        "object": "chat.completion.chunk", 
                        "model": data["model"], 
                        "choices": [{ "delta": {}, "finish_reason": "stop", "index": 0 }]
                    }
            await response.write(f"data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n".encode())
            await response.write_eof()
        return response

app = web.Application()
app.router.add_route('*', '/{path:.*}', handle_request)
web.run_app(app, host='127.0.0.1', port = 41323)    
