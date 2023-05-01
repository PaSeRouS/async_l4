import asyncio
import datetime

import aiofiles


async def tcp_chat():
    reader, writer = await asyncio.open_connection(
        'minechat.dvmn.org',
        5000
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

        async with aiofiles.open('chat.txt', 'a') as chat_file:
            await chat_file.write(output)


def main():
    asyncio.run(tcp_chat())


if __name__ == '__main__':
    main()
