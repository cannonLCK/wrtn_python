'''Simple wrapper util class for API requesting'''
import aiohttp
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass
class Http:
    url:     str  = field(default_factory=str)
    header:  dict = field(default_factory=dict)
    query:   dict = field(default_factory=dict)
    payload: dict = field(default_factory=dict)

class APIRequester:
    '''Simple class for get, post, delete'''
    # session = requests.Session()
    # async_session = aiohttp.ClientSession() 
    def __init__(self, base_url:str, debug=False):
        self.debug = debug
        self.base_url = base_url

    async def _handle_response(self, response, callback:Callable):
        if self.debug:
            print(response.status)
        if 200 <= response.status <= 299:
            if "application/json" in response.headers["Content-Type"]:
                data = await response.json()
                return callback(data) if callback is not None else data
        else:
            raise Exception(response.status)

    async def _handle_event_stream(self, response, callback:Callable):
        if self.debug:
            print(response.status)
        if 200 <= response.status <= 299:
            async for data in response.content.iter_chunks():
                yield callback(data)
                # yield callback(data) if callback is not None else data
        else:
            raise Exception(response.status)
    
    async def _make_request(self, method:str, info:Http, callback = None, timeout:int = 5, **kwargs):
        if self.debug:
            print(f"{method.upper()} request to URL: {self.base_url + info.url}\nParams: {info}\nAdditional: {kwargs}")

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=self.base_url + info.url,
                headers=info.header,
                params=info.query,
                json=info.payload,
                timeout=timeout, **kwargs
            ) as response:
                return await self._handle_response(response, callback)

    async def get(self, info:Http, callback:Optional[Callable] = None):
        return await self._make_request("get", info=info, callback=callback)

    async def post(self, info:Http, callback:Optional[Callable] = None):
        return await self._make_request("post", info=info, callback=callback, timeout=6000000)

    async def delete(self, info:Http, callback:Optional[Callable] = None):
        return await self._make_request("delete", info=info, callback=callback)
    
    async def stream(self, info:Http, callback:Callable):
        '''stream: params = query, json = payload'''
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url + info.url, json=info.payload, params=info.query, headers=info.header, timeout=6000000) as response:
                # return await self._handle_response_stream(response)
                async for res_text in self._handle_event_stream(response, callback=callback):
                    yield res_text
