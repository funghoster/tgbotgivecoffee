import typing

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class WorkerFilter(BoundFilter):
    key = 'is_worker'

    def __init__(self, is_worker: typing.Optional[bool] = None):
        self.is_worker = is_worker

    async def check(self, obj):
        if self.is_worker is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.worker_ids) == self.is_worker
