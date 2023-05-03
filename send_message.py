import asyncio
from argparse import ArgumentParser

from environs import Env


async def send_message(host, port, token):
    reader, writer = await asyncio.open_connection(
        host,
        port
    )

    writer.write(f"{token}\n".encode())
    await writer.drain()

    message = 'Я снова тестирую чатик. Это третье сообщение.'
    
    if not message:
        message = '\n'
    else:
        message = message.replace('\n', '').strip()
        message = f'{message}\n\n'

    writer.write(message.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    


def main():
    parser = ArgumentParser()
    parser.add_argument('--host', help='Адрес чат-сервера')
    parser.add_argument('--port', help='Порт чат-сервера для отправки сообщения')
    parser.add_argument('--token', help='Токен пользоявателя для входа')
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
        port = env('PORT_SEND_MESSAGE')

    if not port:
        print('Укажите порт чат-сервера либо при вызове программы либо в переменных окружения')
        return
    
    if args.token:
        token = args.token
    else:
        token = env('USER_TOKEN')

    if not token:
        text = '''
            Укажите окен пользователя для входа либо при вызове программы либо в переменных окружения
        '''

        print(dedent(text))
        return

    asyncio.run(send_message(host, port, token))

if __name__ == '__main__':
    main()