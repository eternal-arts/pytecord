from typing import Any, Literal

from .interfaces import Object
from .annotations import hash_str
from .utils import get_snowflake, rget

class User(Object):
    def __init__(self, data: dict[str, Any], token: str) -> None:
        self.id: int = get_snowflake('id')
        self.username: str = data.get('username')
        self.discriminator: str | None = data.get('discriminator')
        self.global_name: str | None = data.get('global_name')
        self.avatar: hash_str | None = data.get('avatar')
        self.bot: bool | None = data.get('bot')
        self.system: bool | None = data.get('system')
        self.mfa_enabled: bool | None = data.get('mfa_enabled')
        self.banner: hash_str | None = data.get('banner')
        self.accent_color: int | None = data.get('accent_color')
        self.locale: str | None = data.get('locale')
        self.verified: bool | None = data.get('verified')
        self.email: str | None = data.get('email')
        self.flags: int | None = data.get('flags')
        self.premium_type: int | None = data.get('premium_type')
        self.public_flags: int | None = data.get('public_flags')
        self.avatar_decoration: hash_str | None = data.get('avatar_decoration')

        self.__token = token
        self.__data = data
    
    def eval(self) -> dict[str, Any]:
        """
        Returns a dict representation of user

        ```
        >>> user = User()
        >>> user.eval()
        ```
        """
        return self.__data
    
    def __int__(self) -> int:
        """
        Returns an object id

        ```
        >>> obj = Object()
        >>> int(obj)
        ```
        """
        return self.id


class GuildMember(Object):
    def __init__(self, data: dict[str, Any], token: str) -> None:
        self.user: User | None = User(x, token) if (x := data.get('user')) else None
        self.nick: str | None = data.get('nick')
        self.avatar: str | None = data.get('avatar')
        self.roles: int = data.get('roles')
        self.joined_at: str = data.get('joined_at')
        self.premium_since: str | None = data.get('premium_since')
        self.deaf: bool = data.get('deaf')
        self.mute: bool = data.get('mute')
        self.flags: int = data.get('flags')
        self.pending: bool | None = data.get('pending')
        self.permissions: str | None = data.get('permissions')
        self.communication_disabled_until: str | None = data.get('communication_disabled_until')

        self.__data = data
    
    def __int__(self) -> int | Literal[0]:
        return self.user.id if self.user else 0
    
    def eval(self) -> dict[str, Any]:
        return self.__data
    
    def __str__(self) -> str | Literal['']:
        return self.nick if self.nick else ''
