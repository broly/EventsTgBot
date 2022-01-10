import typing
from dataclasses import dataclass
from datetime import datetime, timedelta

from colorama import Fore, Back

import Config
from Config import NOTIFY_IN_MINS, NOTIFY_CANCEL_IN_HOURS, ACTIVE_AFTER_HAPPENED_MINS
from Text import Text

levels_emoji = {
    0: "0️⃣",
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
}

@dataclass
class Event:
    Topic: str
    Description: str
    Date: datetime
    Levels: list[int]
    Members: list[str]
    CreationState: typing.Optional[str]
    NotificationHappened: bool
    Photo: typing.Optional[bytes]

    def __init__(self):
        self.Topic = "[no topic]"
        self.Description = "[no description]"
        self.Date = datetime.now()
        self.Levels = []
        self.Members = []
        self.id = None
        self.CreationState = None
        self.NotificationHappened = False
        self.active = True
        self.min_members = 0
        self.cancelled = False
        self.Photo = None

    def add_member(self, member: str):
        if member not in self.Members:
            print(f"{Fore.LIGHTBLUE_EX}New member {Fore.LIGHTGREEN_EX}{member}{Fore.LIGHTBLUE_EX} added to event {Back.MAGENTA}{self.Topic}{Back.RESET}{Fore.RESET}")
            self.Members.append(member)
            return True
        return False

    def del_member(self, member: str):
        if member in self.Members:
            print(f"{Fore.LIGHTRED_EX}The member {Fore.LIGHTGREEN_EX}{member}{Fore.LIGHTRED_EX} has been removed from {Back.MAGENTA}{self.Topic}{Back.RESET}{Fore.RESET}")
            self.Members.remove(member)
            return True
        return False

    def set_levels(self, s: str):
        self.Levels = [int(l) for l in s.split(",")]

    def set_notified(self):
        self.NotificationHappened = True
        print(f"{Fore.GREEN}The event {Back.MAGENTA}{self.Topic}{Back.RESET} is coming!")

    def get_datetime(self):
        result = self.Date.strftime('%d/%m/%Y %H:%M (%A)')
        return result

    def get_status_string(self, required_people=0):
        if not self.active and self.cancelled:
            return Text.CLOSED
        if not self.active:
            return Text.TOOK_PLACE
        if self.active:
            if len(self.Members) < self.min_members:
                return Text.MORE_MEMBERS_NEEDED.format(required_people=required_people)
            else:
                if self.NotificationHappened:
                    return Text.WILL_BEGIN_NOW
                else:
                    return Text.OPEN

    def to_text(self):
        br = '\n'
        text_message = Text.EVENT_BODY.format(
            STATUS=self.get_status_string(self.min_members - len(self.Members)),
            TOPIC=self.Topic,
            DATETIME=self.get_datetime(),
            LEVELS=''.join([levels_emoji[n] for n in self.Levels]),
            MIN_MEMBERS=self.min_members,
            PARTY=br.join(self.Members),
            DESCRIPTION=self.Description,
        )

        # text_message = f"SPEAKING CLUB / РАЗГОВОРНЫЙ КЛУБ\n" \
        #                f"{self.get_status_string(self.min_members - len(self.Members))} \n" \
        #                f"<b>{self.Topic}</b>\n\n" \
        #                f"📅 {self.get_datetime()}\n\n" \
        #                f"<i>{self.Description}</i>\n\n" \
        #                f"Levels: {''.join([levels_emoji[n] for n in self.Levels])}\n" \
        #                f"👤 We need {self.min_members}+ members\n"\
        #                f"👥 Party:\n {br.join(self.Members)}\n\n" \
        #                f"To participate type: <code>+{self.Topic}</code>\n"\
        #                f"To leave: <code>-{self.Topic}</code>\n\n"
        return text_message


    def should_notify(self):
        return not self.NotificationHappened and self.Date - timedelta(minutes=NOTIFY_IN_MINS) < datetime.now()

    def is_already_happened(self):
        return datetime.now() > (self.Date + timedelta(minutes=ACTIVE_AFTER_HAPPENED_MINS))

    def should_be_cancelled(self):
        return len(self.Members) < self.min_members and (self.Date - timedelta(hours=NOTIFY_CANCEL_IN_HOURS)) < datetime.now()

    def print(self):
        members = ', '.join(self.Members)
        diff = self.Date - datetime.now()
        print(f"{Fore.LIGHTBLUE_EX}Planned event {Back.MAGENTA}{self.Topic}{Back.RESET} at date {Fore.LIGHTMAGENTA_EX}{self.get_datetime()}{Fore.LIGHTBLUE_EX}. \n"
              f"   Members: {Fore.LIGHTGREEN_EX}{members if members else Fore.CYAN + 'nobody yet :)'}{Fore.LIGHTBLUE_EX} \n"
              f"   Levels: {Fore.YELLOW}{', '.join([str(level) for level in self.Levels])}{Fore.LIGHTBLUE_EX}\n" +
              (f"   Will happened after {Fore.LIGHTCYAN_EX}{diff.days}{Fore.LIGHTBLUE_EX} days since this moment{Back.RESET}" if diff.days else
              f"   Will happened {Fore.LIGHTCYAN_EX}today{Fore.LIGHTBLUE_EX}"))
        print()

    def pending_removal(self):
        print(f"{Fore.LIGHTRED_EX}The event {Back.MAGENTA}{self.Topic}{Back.RESET} is pending to remove{Fore.RESET}")