from dataclasses import dataclass
from typing import List, AsyncGenerator
from urllib.parse import urlparse

from grpclib.client import Channel

import functionsdk
from functionsdk import APIGatewayServiceStub, ChatCompleteResponse, EmbedResponse, ImageQuality, TranscribeResponse
from functionsdk import ChatCompleteMessage
from functionsdk import TextToImageResponseImage

DEFAULT_BASE_PATH = "https://api.function.network"
"""
The default Function Network API gateway base URL.
"""

@dataclass
class ClientOptions:
    """
    Options used to configure a Function Network client.
    """

    apiKey: str
    """
    The API key used to authenticate calls made to the network.
    """

    baseUrl: str = DEFAULT_BASE_PATH
    """
    The Function Network API gateway base URL.
	If unspecified, defaults to DefaultBaseUrl.
	Most users will not need to specify a value here.
    """

async def _chat_complete_stream_wrapper(base: AsyncGenerator[functionsdk.ChatCompleteStreamResponse, None]) -> AsyncGenerator[str, None]:
    async for chunk in base:
        yield chunk.response.content
    raise StopAsyncIteration

@dataclass
class ChatCompleteStreamResponse:
    """
    A streaming response for ChatCompleteStream.
    The response includes the role of the response message, and an AsyncGenerator of output tokens.
    """

    role: str
    """
    The role for the response message.
    """

    tokenStream: AsyncGenerator[str, None]
    """
    An AsyncGenerator of output tokens.
    """

class Client:
    """
    A client that can interact with the Function Network.
    Clients contain authentication information and can make inference calls.
    """

    _service: APIGatewayServiceStub = None

    def __init__(self, options: ClientOptions):
        if options.apiKey == "" or options.apiKey is None:
            raise ValueError("apiKey must be specified")

        url = urlparse(options.baseUrl)
        channel = Channel(
            host=url.hostname,
            port=url.port,
            path=url.path,
            ssl=url.scheme == "https",
        )
        self.service = APIGatewayServiceStub(channel, metadata=[('x-api-key', options.apiKey)])

    async def chat_complete(self, model: str, messages: List[ChatCompleteMessage]) -> ChatCompleteResponse:
        """
        Takes in a list of messages, each with a role and content, and generates the next reply in the chain.
        The entire response is returned at once in a blocking fashion with this function.
        The response token count is returned with the response.
        If you would like to stream each token as it is generated, use ChatCompleteStream instead.

        Please refer to the developer docs to find a suitable model to use.
        """

        return await self.service.chat_complete(model=model, message=messages)

    async def chat_complete_stream(self, model: str, messages: List[ChatCompleteMessage]) -> ChatCompleteStreamResponse:
        """
        Takes in a list of messages, each with a role and content, and generates the next reply in the chain.
        The response is streamed as each token is generated.
        If you would like to get the entire response at once, use ChatComplete instead.

        Please refer to the developer docs to find a suitable model to use.
        """

        raw = self.service.chat_complete_stream(model=model, message=messages)

        # Read the first chunk to get the role.
        # Note that res is an AsyncGenerator.
        first = await raw.__anext__()

        role = first.response.role

        return ChatCompleteStreamResponse(
            role=role,
            tokenStream=_chat_complete_stream_wrapper(raw),
        )

    async def embed(self, model: str, input_string: str) -> EmbedResponse:
        """
        Takes in input string(s) and returns the generated vector embeddings.

        Please refer to the developer docs to find a suitable model to use.
        """

        return await self.service.embed(model=model, input=input_string)

    async def text_to_image(self, model: str, prompt: str, count: int, quality: ImageQuality, size: str) -> List[TextToImageResponseImage]:
        """
        Takes in a text prompt and some parameters and generates an image based on the input prompt.
        The image is returned as a downloadable URL.
        Returned image URLs are not guaranteed to be available indefinitely, so they should not be treated as long-term CDN URLs.

        Please refer to the developer docs to find a suitable model to use.
        """

        res = await self.service.text_to_image(model=model, prompt=prompt, count=count, quality=quality, size=size)
        return res.images

    async def transcribe(self, model: str, url: str) -> TranscribeResponse:
        """
        Takes in an audio URL and transcribes it into text.
        The transcribed text is returned as a string.

        Please refer to the developer docs to find a suitable model to use.
        """

        return await self.service.transcribe(model=model, url=url)
