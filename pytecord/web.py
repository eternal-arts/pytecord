from pytecord.interfaces import BaseDataStreamListener

from typing import Callable, Coroutine, Any
from aiohttp import ClientSession
from datetime import datetime
from time import mktime
from asyncio import gather, create_task
from asyncio import sleep as asleep

class ApiRequest:
    ...


class ApiConnector:
    def __init__(self, api_version: int) -> None:
        self.base_url = f'https://discord.com/api/v{api_version}'

    def try_request(self, request: ApiRequest):
        ...


class GatewayRequest:
    def __init__(self, op: int = None, d: dict[str, Any] = None, s: int = None, t: str = None, *, data: dict[str, Any] = None) -> None:
        if data:
            op = data['op']
            d = data['d']
            s = data['s']
            t = data['t']

        self.op = op
        self.d = d
        self.s = s
        self.t = t

    def __repr__(self) -> str:
        return f'GatewayRequest(op={self.op}, d={self.d}, s={self.s}, t={self.t})'

    def eval(self):
        return {
            'op': self.op,
            'd': self.d,
            's': self.s,
            't': self.t
        }

    def __getitem__(self, key: str):
        return self.eval()[key]


class GatewayOutput(GatewayRequest): ... # For typing


class DataStreamListener:
    def __init__(self, events: dict[str, Callable[[GatewayRequest], Coroutine[Any, Any, Any]]] = {}) -> None:
        self.events = events

    async def listen(self, request: GatewayRequest):
        if self.events.get(request.t):
            await self.events.get(request.t)(request)


class DataStream:
    def __init__(
            self,
            listener: BaseDataStreamListener,
            gateway_version: int,
            headers: dict,
            token: str,
            intents: int = 0,
            afk: bool = False,
            status: str = 'online',
            activities: list[dict] = []
        ) -> None:
        self.listener = listener
        self._ws = None
        self.gateway_version = gateway_version
        self.headers = headers

        self.running = False

        self.token = token
        self.intents = intents

        self.afk = afk
        self.status = status
        self.activities = activities

    async def receive_response(self) -> GatewayOutput | None:
        try:
            j = await self._ws.receive_json()
            return GatewayOutput(data=j) if j else None
        except TypeError:
            return None
    
    async def send_request(self, data: GatewayRequest) -> dict:
        await self._ws.send_json(data.eval())
        return GatewayRequest(data)
    
    async def identify(self):
        await self.send_request(GatewayRequest(
            op=2,
            d={
                'token': self.token,
                'intents': self.intents,
                'properties': {
                    'os': 'windows',
                    'browser': 'pytecord',
                    'device': 'pytecord'
                },
                'presence': {
                    'since': mktime(datetime.now().timetuple()) * 1000,
                    'afk': self.afk,
                    'status': self.status,
                    'activities': self.activities
                }
            }
        ))
    
    async def life(self, heartbeat_interval: float):
        while self.running:
            await self.send_request(GatewayRequest(1))

            await asleep(heartbeat_interval)
    
    async def check_events(self):
        while self.running:
            if data := await self.receive_response():
                ...
            else:
                continue
            await self.listener.listen(data)

    async def run(self):
        self.running = True

        async with ClientSession(headers=self.headers) as session:
            async with session.ws_connect(
                f"wss://gateway.discord.gg/?v={self.gateway_version}&encoding=json"
            ) as ws:
                self._ws = ws

                data = await self.receive_response()
                await self.identify()

                await gather(
                    create_task(self.life(data['d']['heartbeat_interval'] / 1000)),
                    create_task(self.check_events())
                )


class BaseWebhook:
    def __init__(self, token: str) -> None:
        self.token = token
        self.headers = {'Authorization': f'Bot {self.token}',}

        self.listener = DataStreamListener()
        self.stream = DataStream(self.listener, 10, self.headers, self.token)
        self.api_connector = ApiConnector(10)

    def add_event(self, event_type:str, function: Callable):
        self.listener.events[event_type] = function

    async def run(self):
        await self.stream.run()