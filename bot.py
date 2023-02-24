import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.worker import WorkerFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.worker import register_worker
from tgbot.handlers.user import register_user
from tgbot.handlers.user_register import register_user_register
from tgbot.handlers.order_coffee import register_handlers_drinks
from tgbot.handlers.order_tea import register_handlers_tea
from tgbot.handlers.user_order import register_user_order
from tgbot.handlers.bot_info import register_bot_info
from tgbot.handlers.echo import register_echo
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.misc import db



logger = logging.getLogger(__name__)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/neworder", description="Сделать заказ"),
        BotCommand(command="/basket", description="Заказы")
    ]
    await bot.set_my_commands(commands)  

def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(WorkerFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_worker(dp)
    register_user(dp)
    register_user_register(dp)
    register_handlers_drinks(dp)
    register_handlers_tea(dp)
    register_user_order(dp)  
    register_bot_info(dp)  
    register_echo(dp)



async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")
    db.sql_start()

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)
   

    # start
    try: 
        await set_commands(bot)
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
