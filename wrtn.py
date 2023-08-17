'''
wrtn.py
reverse proxy api for wrtn
'''
import json
from util import Http, APIRequester
from fake_useragent import UserAgent
import inspect

class ChunkDecoder:
    def __init__(self):
        self.buffer = ""

    def decode(self, chunk_tuple):
        for chunk in chunk_tuple:
            if(isinstance(chunk, bytes)):
                return self.decode_chunks(chunk)
                
    def decode_chunks(self, chunk_byte):
        chunk_str = self.buffer + chunk_byte.decode(encoding="utf-8", errors="ignore")
        chunks = chunk_str.split('\n\n')
        last_chunk = chunks[-1]
        self.buffer = "" if last_chunk == "" else last_chunk
        json_objects = [json.loads((line.split(": ", 1)[1])) 
                        for line in chunks[:-1] if line.strip().startswith('data: {')]
        res_text = "".join(obj['chunk'] for obj in json_objects if 'chunk' in obj if obj['chunk'] is not None)
        return res_text

#TODO: Divide WrtnAPI to Chat, Studio, Tool/ChatBot
class WrtnAPI:
    '''
    WrtnAPI: needs json path
    '''
    def __init__(self, debug = False) -> None:
        self.debug = debug
        self.header = {
            "Init": {
                "Refresh": "",
                "Content-Type": "application/json"
            },
            "Auth": {
                "User-Agent": UserAgent().safari
            },
        }
        self.wrtn_requester = APIRequester("https://api.wow.wrtn.ai", debug=debug)
        self.wrtn_studio_requester = APIRequester("https://studio-api.wow.wrtn.ai", debug=debug)
    
    async def login(self, account):
        response = await self.wrtn_requester.post(
            info=Http(
                url="/auth/local",
                header=self.header["Init"],
                payload={
                    "email": account['id'],
                    "password": account['pw']
                },
            ),
        )
        self.header["Init"] |= {"Refresh": response['data']['refreshToken']}
        return response['data']['refreshToken']
    
    async def access_token(self):
        '''refresh access_token with refresh_key'''
        response = await self.wrtn_requester.post(
            info=Http(
                url="/auth/refresh",
                header=self.header["Init"],
            ),
        )
        return {"Authorization": "Bearer " + response['data']['accessToken']}

    async def chat_by_json(self, _id: str, msg: str, oldmsg: list[dict], model:str='gpt-3.5-turbo'):
        '''chat method with json. currently: gpt-3.5 and gpt-4, context length is unknown'''

        self.header["Auth"] |= await self.access_token()
        decoder = ChunkDecoder()
        async for response in self.wrtn_studio_requester.stream(
            info=Http(
                url=f"/store/chat-bot/{_id}/generate", 
                header=self.header["Auth"],
                payload={
                    "content": msg,
                    "model": model,
                    "oldMessages": oldmsg,
                },
            ), callback=decoder.decode
        ):
            yield response
        await self.delete_chatbot(_id)

    async def get_chatbot(self) -> list:
        '''loads all chatbots from this user'''


        self.header["Auth"] |= await self.access_token()
        response = await self.wrtn_studio_requester.get(
            info=Http(
                url="/studio/chat-bot",
                header=self.header["Auth"]
            ),
        )
        return response['data']
    
    async def delete_chatbot(self, _id: str):
        '''delete a chatbot with specific id. You must delete your chatbot after use.'''


        self.header["Auth"] |= await self.access_token()
        response = await self.wrtn_studio_requester.delete(
            info=Http(
                url=f"/studio/chat-bot/{_id}",
                header=self.header["Auth"],
            ),
        )
        return response
    
    async def get_tool(self) -> list:
        '''loads all tools from this user'''

            
        self.header["Auth"] |= await self.access_token()
        response = await self.wrtn_studio_requester.get(
            info=Http(
                url="/studio/tool", 
                header=self.header["Auth"],
            ),
        )
        return response['data']
    
    async def delete_tool(self, _id: str):
        '''delete a tool with specific id. You must delete your chatbot after use.'''

        
        self.header["Auth"] |= await self.access_token()
        response = await self.wrtn_studio_requester.delete(
            info=Http(
                url=f"/studio/tool/{_id}",
                header=self.header["Auth"],
            ),
        )
        return response
        
    async def make_chatbot(self):
        '''
        make a chatbot with specific option.
        Must register a chatbot with passing an toxicity test, to use a json prompt with system role.
        '''
        # toolList = await self.get_tool()
        # for tool in toolList['toolList']:
        #     await self.delete_tool(tool['id'])
        # chatBotList = await  self.get_chatbot()
        # for chatBot in chatBotList['chatBotList']:
        #     await self.delete_chatbot(chatBot['id'])


        self.header["Auth"] |= await self.access_token()
        payload = {
            "difficulty":"hard",
            "icon":"faceSmile",
            "title":" ",
            "description":" ",
            "category":[" "],
            "firstMessage":" ",
            "selectTypeForExampleQuestion":" ",
            "exampleQuestion":[""],
            "promptForEasy":{
                "role":"","personality":"","requirement":""
            },
            "promptForDifficult":"",
            "userName":" ",
            "isDeleted":False,
            # "additionalInformation": "",
            "isTemporarySave":False,
            "openType":"비공개",
            "priceType":"무료",
        }
        response = await self.wrtn_studio_requester.post(
            info=Http(
                url="/studio/chat-bot",
                header=self.header["Auth"],
            ),
        )
        
        _id = response['data']['chatBotList'][0]['id']
        payload["userId"] = response['data']['chatBotList'][0]['userId']
        payload["chatBotId"] = _id
        chatbot = await self.wrtn_studio_requester.post(
            info=Http(
                url=f"/studio/chat-bot/{_id}",
                payload=payload,
                header=self.header["Auth"],
            ),
        )
        return chatbot['data']['chatBotList'][0]['id']