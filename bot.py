from colorama import *
from datetime import datetime, timedelta
from fake_useragent import FakeUserAgent
from faker import Faker
from urllib.parse import parse_qs
import aiohttp, asyncio, json, os, random, re, sys

class Major:
    def __init__(self) -> None:
        self.faker = Faker()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Host': 'major.bot',
            'Pragma': 'no-cache',
            'Referer': 'https://major.bot/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': FakeUserAgent().random
        }
        self.print_ascii_banner()

    def print_ascii_banner(self):
        print(r"""

,---.    ,---.   ____         .-./`)     ,-----.    .-------.
|    \  /    | .'  __ `.      \ '_ .') .'  .-,  '.  |  _ _   \
|  ,  \/  ,  |/   '  \  \    (_ (_) _)/ ,-.|  \ _ \ | ( ' )  |
|  |\_   /|  ||___|  /  |      / .  \;  \  '_ /  | :|(_ o _) /
|  _( )_/ |  |   _.-`   | ___  |-'`| |  _`,/ \ _/  || (_,_).' _
| (_ o _) |  |.'   _    ||   | |   ' : (  '\_/ \   ;|  |\ \  | |
|  (_,_)  |  ||  _( )_  ||   `-'  /   \ `"/  \  ) / |  | \ `'  /
|  |      |  |\ (_ o _) / \      /     '. \_/``".'  |  |  \   /
'--'      '--' '.(_,_).'   `-..-'        '-----'    ''-'   `-'
                                                                  
    Auto Claim Bot For  Major - MR X CRIMINAL
    Author  : MR-X
        """)
        self.print_timestamp("[ System Initialized ]")

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_timestamp(self, message):
        print(
            f"{Fore.BLUE + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def load_queries(self, file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def process_queries(self, lines_per_file: int):
        if not os.path.exists('data.txt'):
            raise FileNotFoundError(f"File 'data.txt' not found. Please ensure it exists.")

        with open('data.txt', 'r') as f:
            queries = [line.strip() for line in f if line.strip()]
        if not queries:
            raise ValueError("File 'data.txt' is empty.")

        existing_queries = set()
        for file in os.listdir():
            if file.startswith('queries-') and file.endswith('.txt'):
                with open(file, 'r') as qf:
                    existing_queries.update(line.strip() for line in qf if line.strip())

        new_queries = [query for query in queries if query not in existing_queries]
        if not new_queries:
            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ No New Queries To Add ]{Style.RESET_ALL}")
            return

        files = [f for f in os.listdir() if f.startswith('queries-') and f.endswith('.txt')]
        files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

        last_file_number = int(re.findall(r'\d+', files[-1])[0]) if files else 0

        for i in range(0, len(new_queries), lines_per_file):
            chunk = new_queries[i:i + lines_per_file]
            if files and len(open(files[-1], 'r').readlines()) < lines_per_file:
                with open(files[-1], 'a') as outfile:
                    outfile.write('\n'.join(chunk) + '\n')
                self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Updated '{files[-1]}' ]{Style.RESET_ALL}")
            else:
                last_file_number += 1
                queries_file = f"queries-{last_file_number}.txt"
                with open(queries_file, 'w') as outfile:
                    outfile.write('\n'.join(chunk) + '\n')
                self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Generated '{queries_file}' ]{Style.RESET_ALL}")

    async def generate_token(self, query: str):
        url = 'https://major.bot/api/auth/tg/'
        data = json.dumps({'init_data':query})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json',
            'Origin': 'https://major.bot'
        }
        try:
            await asyncio.sleep(random.randint(3, 5))
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.post(url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    tg_auth = await response.json()
                    parsed_query = parse_qs(query)
                    user_data_json = parsed_query['user'][0]
                    user_data = json.loads(user_data_json)
                    token = f"Bearer {tg_auth['access_token']}"
                    id = user_data['id']
                    name = user_data.get('first_name', self.faker.user_name())
                    return (token, id, name)
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError, Exception) as e:
            self.print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ Failed To Process {query} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}"
            )
            return None

    async def generate_tokens(self, queries):
        tasks = [self.generate_token(query) for query in queries]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def visit(self, token: str):
        url = 'https://major.bot/api/user-visits/visit/'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': '0',
            'Content-Type': 'application/json',
            'Origin': 'https://major.bot'
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers) as response:
                    if response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Major Down While Daily Visit ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    visit = await response.json()
                    if visit['is_increased']:
                        if visit['is_allowed']:
                            return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Claimed Daily Visit ]{Style.RESET_ALL}")
                        return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Subscribe Major Community To Claim Your Daily Visit Bonus And Increase Your Streak ]{Style.RESET_ALL}")
                    return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Daily Visit Already Claimed ]{Style.RESET_ALL}")
        except aiohttp.ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Daily Visit: {str(e)} ]{Style.RESET_ALL}")
        except (Exception, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Daily Visit: {str(e)} ]{Style.RESET_ALL}")

    async def streak(self, token: str):
        url = 'https://major.bot/api/user-visits/streak/'
        headers = {
            **self.headers,
            'Authorization': token
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers) as response:
                    if response.status in [500, 520]:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Major Down While Fetching Streak ]{Style.RESET_ALL}")
                        return None
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientResponseError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Streak: {str(e)} ]{Style.RESET_ALL}")
            return None
        except (Exception, aiohttp.ContentTypeError) as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Streak: {str(e)} ]{Style.RESET_ALL}")
            return None

    async def user(self, token: str, id: str):
        url = f'https://major.bot/api/users/{id}/'
        headers = {
            **self.headers,
            'Authorization': token
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers) as response:
                    if response.status in [500, 520]:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Major Down While Fetching User ]{Style.RESET_ALL}")
                        return None
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientResponseError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching User: {str(e)} ]{Style.RESET_ALL}")
            return None
        except (Exception, aiohttp.ContentTypeError) as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching User: {str(e)} ]{Style.RESET_ALL}")
            return None

    async def join_squad(self, token: str):
        url = f'https://major.bot/api/squads/2245008508/join/'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': '0',
            'Origin': 'https://major.bot'
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers) as response:
                    response.raise_for_status()
                    join_squad = await response.json()
                    if join_squad['status'] == 'ok': return True
        except (Exception, aiohttp.ClientResponseError, aiohttp.ContentTypeError):
            return False

    async def leave_squad(self, token: str):
        url = f'https://major.bot/api/squads/leave/'
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': '0',
            'Origin': 'https://major.bot'
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers) as response:
                    response.raise_for_status()
                    leave_squad = await response.json()
                    if leave_squad['status'] == 'ok': return await self.join_squad(token=token)
        except (Exception, aiohttp.ClientResponseError, aiohttp.ContentTypeError):
            return False

    async def tasks(self, token: str, type: str):
        url = f'https://major.bot/api/tasks/?is_daily={type}'
        headers = {
            **self.headers,
            'Authorization': token
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers) as response:
                    if response.status in [500, 520]:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Major Down While Fetching Tasks ]{Style.RESET_ALL}")
                        return None
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientResponseError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
            return None
        except (Exception, aiohttp.ContentTypeError) as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
            return None

    async def complete_task(self, token: str, task_title: str, task_award: int, payload: dict):
        url = 'https://major.bot/api/tasks/'
        data = json.dumps(payload)
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json',
            'Origin': 'https://major.bot'
        }
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 400: return
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Major Down While Complete Tasks ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    complete_task = await response.json()
                    if complete_task['is_completed']:
                        return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ You\'ve Got {task_award} From {task_title} ]{Style.RESET_ALL}")
                    return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ {task_title} Isn\'t Completed ]{Style.RESET_ALL}")
        except aiohttp.ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Complete Tasks: {str(e)} ]{Style.RESET_ALL}")
        except (Exception, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Complete Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def task_answer(self):
        url = 'https://raw.githubusercontent.com/Shyzg/major/refs/heads/main/answer.json'
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    response_answer = json.loads(await response.text())
                    return response_answer['youtube']
        except aiohttp.ClientResponseError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Get Task Answer: {str(e)} ]{Style.RESET_ALL}")
            return None
        except (Exception, aiohttp.ContentTypeError) as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Get Task Answer: {str(e)} ]{Style.RESET_ALL}")
            return None

    async def main(self, queries: str):
        while True:
            try:
                accounts = await self.generate_tokens(queries=queries)
                total_rating = 0

                for (token, id, name) in accounts:
                    self.print_timestamp(
                        f"{Fore.WHITE + Style.BRIGHT}[ Information ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}[ {name} ]{Style.RESET_ALL}"
                    )
                    await self.visit(token=token)
                    streak = await self.streak(token=token)
                    await asyncio.sleep(random.randint(3, 5))
                    user = await self.user(token=token, id=id)
                    await asyncio.sleep(random.randint(3, 5))
                    if user is not None:
                        self.print_timestamp(
                            f"{Fore.GREEN + Style.BRIGHT}[ Balance {user['rating']} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}[ Streak {streak['streak'] if streak else 0} ]{Style.RESET_ALL}"
                        )
                        if user['squad_id'] is None:
                            await self.join_squad(token=token)
                            await asyncio.sleep(random.randint(3, 5))
                        elif user['squad_id'] != 2245008508:
                            await self.leave_squad(token=token)
                            await asyncio.sleep(random.randint(3, 5))

                for (token, id, name) in accounts:
                    self.print_timestamp(
                        f"{Fore.WHITE + Style.BRIGHT}[ Games ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}[ {name} ]{Style.RESET_ALL}"
                    )

                for (token, id, name) in accounts:
                    self.print_timestamp(
                        f"{Fore.WHITE + Style.BRIGHT}[ Tasks ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}[ {name} ]{Style.RESET_ALL}"
                    )
                    for type in ['true', 'false']:
                        tasks = await self.tasks(token=token, type=type)
                        await asyncio.sleep(random.randint(3, 5))
                        if tasks is not None:
                            for task in tasks:
                                if not task['is_completed']:
                                    if task['type'] == 'code':
                                        task_answer = await self.task_answer()
                                        if task_answer is not None:
                                            if task['title'] in task_answer:
                                                answer = task_answer[task['title']]
                                                await self.complete_task(token=token, task_title=task['title'], task_award=task['award'], payload={"task_id":task['id'],"payload":{'code':answer}})
                                                await asyncio.sleep(random.randint(3, 5))
                                    else:
                                        await self.complete_task(token=token, task_title=task['title'], task_award=task['award'], payload={"task_id":task['id']})
                                        await asyncio.sleep(random.randint(3, 5))
                    user = await self.user(token=token, id=id)
                    await asyncio.sleep(random.randint(3, 5))
                    total_rating += user['rating'] if user else 0

                self.print_timestamp(
                    f"{Fore.CYAN + Style.BRIGHT}[ Total Account {len(accounts)} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Total Rating {total_rating} ]{Style.RESET_ALL}"
                )

                sleep_timestamp = (datetime.now().astimezone() + timedelta(seconds=1800)).strftime('%X %Z')
                self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting At {sleep_timestamp} ]{Style.RESET_ALL}")

                await asyncio.sleep(1800)
                self.clear_terminal()
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
                continue

if __name__ == '__main__':
    try:
        if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        init(autoreset=True)
        major = Major()

        data_file = 'data.txt'
        if not os.path.isfile(data_file):
            raise FileNotFoundError(f"No '{data_file}' found.")

        major.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Loading Queries from '{data_file}' ]{Style.RESET_ALL}")
        
        # Load all queries from 'data.txt' directly
        queries = major.load_queries(data_file)

        # Execute the main process with loaded queries
        asyncio.run(major.main(queries=queries))

    except (ValueError, IndexError, FileNotFoundError) as e:
        major.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(0)
