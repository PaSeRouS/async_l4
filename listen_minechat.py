import asyncio
import datetime
import pathlib
from argparse import ArgumentParser
from textwrap import dedent

import aiofiles
from environs import Env


async def tcp_chat(host, port, history):
    reader, writer = await asyncio.open_connection(
        host,
        port
    )

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


def main():
    parser = ArgumentParser()
    parser.add_argument('--host', help='Адрес чат-сервера')
    parser.add_argument('--port', help='Порт чат-сервера')
    parser.add_argument('--history', type=pathlib.Path, help='Путь к файлу с историей чата')
    args = parser.parse_args()

    env = Env()
    env.read_env()

    if args.host:
        host = args.host
    else:
        host = env('HOST')

    if not host:
        print('Укажите адрес чат-сервера либо при вызове программы либо в переменных окружения')
        return

    if args.port:
        port = args.port
    else:
        port = env('PORT')

    if not port:
        print('Укажите порт чат-сервера либо при вызове программы либо в переменных окружения')
        return
    
    if args.history:
        history = args.history
    else:
        history = env('HISTORY')

    if not history:
        text = '''
            Укажите путь к файлу с историей чата либо при вызове программы либо в переменных окружения
        '''

        print(dedent(text))
        return

    asyncio.run(tcp_chat(host, port, history))


if __name__ == '__main__':
    main()
