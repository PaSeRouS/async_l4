import asyncio
import json
import logging
import uuid
from argparse import ArgumentParser

import aiofiles
from environs import Env


log = logging.getLogger(__file__)


async def register(host, port, username, message):
    reader, writer = await asyncio.open_connection(host, port)

    signin_message = (await reader.readline()).decode().strip()
    log.debug(f"Сообщение: {signin_message}")
    skip_auth_reply = "\n"
    writer.write(skip_auth_reply.encode())
    await writer.drain()
    log.debug(f"Ответ: {skip_auth_reply.strip()}")

    request_username_message = (await reader.readline()).decode().strip()
    log.debug(f"Сообщение: {request_username_message}")
    username_reply = f"{username}\n"
    writer.write(username_reply.encode())
    await writer.drain()
    
    log.debug(f"Ответ: {username_reply.strip()}")

    signup_result = json.loads((await reader.readline()).decode())

    log.debug(f"Сообщение: {signup_result}")
    print(f"Зарегестрирован пользователь {signup_result['nickname']}. Вот ваш токен:")
    print(signup_result['account_hash'])

    async with aiofiles.open('token.txt', 'w') as token_file:
        await token_file.write(signup_result['account_hash'])
        print("Токен сохранён в файл token.txt")

    writer.close()
    await writer.wait_closed()

    await authorise(host, port, signup_result['account_hash'], message)


async def authorise(host, port, token, message):
    print('1')
    reader, writer = await asyncio.open_connection(
        host,
        port
    )

    log.debug(await reader.readline())
    writer.write(f"{token}\n".encode())
    await writer.drain()
    log.debug(f"Отправлен токен: {token.strip()}")
    
    auth_result = json.loads((await reader.readline()).decode())
    log.debug(f"Сообщение: {auth_result}")

    if not auth_result:
        writer.close()
        await writer.wait_closed()
        log.debug("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
        return
    
    log.debug(f"Logged in as {auth_result['nickname']}")
    
    await submit_message(writer, message)
    writer.close()
    await writer.wait_closed()


async def submit_message(writer, message):
    if not message:
        message = '\n'
    else:
        message = message.replace('\n', '').strip()
        message = f'{message}\n\n'

    writer.write(message.encode())
    await writer.drain()
    log.debug(f'Отправлено сообщение: {message.strip()}')    


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument(
        '--host',
        help='Адрес чат-сервера'
    )
    
    parser.add_argument(
        '--port',
        help='Порт чат-сервера для отправки сообщения'
    )
    
    parser.add_argument(
        '--user',
        help='Токен пользователя для входа или имя для регистрации'
    )

    parser.add_argument(
        '--message',
        required=True,
        help='Сообщение в чат'
    )
    
    args = parser.parse_args()

    env = Env()
    env.read_env()

    if args.host:
        host = args.host
    else:
        host = env('HOST')

    if not host:
        log.debug('Укажите адрес чат-сервера')
        return

    if args.port:
        port = args.port
    else:
        port = env('PORT_SEND_MESSAGE')

    if not port:
        log.debug('Укажите порт чат-сервера')
        return
    
    token = ''
    if args.user:
        try:
            token = uuid.UUID(args.user)
        except ValueError:
            username = args.user
    else:
        token = env('USER_TOKEN')

        if not token:
            text = '''
                Укажите токен пользователя для входа, либо имя пользователя для регистрации
            '''

            log.debug(dedent(text))
            return

    message = args.message

    if token:
        asyncio.run(authorise(host, port, token, message))
    else:
        asyncio.run(register(host, port, username, message))

if __name__ == '__main__':
    main()