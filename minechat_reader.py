import asyncio
import datetime
import logging
import pathlib
import socket
from argparse import ArgumentParser
from textwrap import dedent
from time import sleep

import aiofiles
import requests
from environs import Env

log = logging.getLogger(__file__)


async def read_chat(host, port, history):
    reader = None
    writer = None

    while True:
        try:
            reader, writer = await asyncio.open_connection(
                host,
                port
            )

            try:
                today = datetime.datetime.now()
                today_str = today.strftime('%d.%m.%Y %H:%M')
                print(f'[{today_str}] Установлено соединение!')

                while not reader.at_eof():
                    today = datetime.datetime.now()
                    today_str = today.strftime('%d.%m.%Y %H:%M')

                    data = await reader.readline()
                    data = data.decode()

                    output = f'[{today_str}] {data}'
                    print(output)

                    async with aiofiles.open(history, 'a') as chat_file:
                        await chat_file.write(output)
            finally:
                writer.close()
                await writer.wait_closed()
        except socket.gaierror:
            log_message = 'Ошибка при подключении к интернету. '
            log_message += 'Следующая попытка через 15 минут.'

            log.warning(log_message)
            sleep(10)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('--host', help='Адрес чат-сервера')
    parser.add_argument('--port', help='Порт чат-сервера')
    parser.add_argument('--history', type=pathlib.Path, help='Путь к файлу с историей чата')
    args = parser.parse_args()

    env = Env()
    env.read_env()

    host = args.host or env('HOST')

    if not host:
        log.debug('Укажите адрес чат-сервера либо при вызове программы либо в переменных окружения')
        return

    port = args.port or env('PORT')

    if not port:
        log.debug('Укажите порт чат-сервера либо при вызове программы либо в переменных окружения')
        return
    
    history = args.history or env("HISTORY")
    
    if not history:
        text = '''
            Укажите путь к файлу с историей чата либо при вызове программы либо в переменных окружения
        '''

        log.debug(dedent(text))
        return

    asyncio.run(read_chat(host, port, history))


if __name__ == '__main__':
    main()
