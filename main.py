try:
    import aiogram
except ImportError:
    from pip._internal import main as pip
    pip(['install', 'aiogram'])
    import aiogram

try:
    import colorama
except ImportError:
    from pip._internal import main as pip
    pip(['install', 'colorama'])
    import colorama


from aiogram.utils import executor
from Bot import EvRegBot
import os

def start():
    from colorama import init
    from colorama import Fore, Back, Style

    init()

    os.system('cls')

    print(f"{Fore.LIGHTYELLOW_EX}Hello! I'm chat telegram bot for planning events in Speak! group")
    print(f"{Fore.LIGHTGREEN_EX}You can do next things:")
    print(f"{Fore.LIGHTCYAN_EX}/IamYOURhost!!!   {Fore.LIGHTMAGENTA_EX} - first thing that you should to do if you want to communicate with me")
    print(f"{Fore.LIGHTCYAN_EX}/event            {Fore.LIGHTMAGENTA_EX} - to start event creation")
    print(f"{Fore.LIGHTCYAN_EX}/cancel           {Fore.LIGHTMAGENTA_EX} - to cancel event creation")
    print(f"{Fore.LIGHTCYAN_EX}/stop             {Fore.LIGHTMAGENTA_EX} - to stop previously created event with specified reason")
    print(f"{Fore.LIGHTCYAN_EX}/clear            {Fore.LIGHTMAGENTA_EX} - to stop all created events")
    print(f"{Fore.LIGHTCYAN_EX}/invite           {Fore.LIGHTMAGENTA_EX} - to invite someone: you should type something like: {Fore.GREEN}/invite @thebroly words{Back.RESET}")
    print(f"{Fore.LIGHTCYAN_EX}/kick             {Fore.LIGHTMAGENTA_EX} - to kick someone from event. Same as /invite: {Fore.GREEN}/kick @thebroly words{Back.RESET}")
    print(Fore.WHITE)
    EvRegBot().start()

if __name__ == '__main__':
    start()
