import asyncio
import datetime
import json
import pickle
import random
import typing
from time import strptime, mktime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from Common import Singleton
from Config import TOKEN, chat_id, NOTIFY_IN_MINS
from Event import Event
from dataclasses import dataclass

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from Text import Text
from colorama import Fore, Back


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


class CancelEventSession:
    event: typing.Optional[Event]
    reason: typing.Optional[str]
    topic_name: typing.Optional[str]

    def __init__(self):
        self.event = None
        self.reason = None
        self.topic_name = None
        self.users = list()


class EvRegBot(metaclass=Singleton):
    events: list[Event]
    sessions: dict[int, Event]
    stop_sessions: dict[int, CancelEventSession]
    users: list[int]
    wrong_users: list[int]

    def __init__(self):
        self.events = []
        self.sessions = {}
        self.stop_sessions = {}
        self.users = []
        self.wrong_users = []
        self.load_state()

    def start(self):
        executor.start_polling(dp, on_startup=self.create_events_check)

    async def create_events_check(self, dispatcher):
        asyncio.create_task(self.check_events())

    def save_state(self):
        with open("events.dat", 'wb') as f:
            f.write(pickle.dumps(self.events))

        with open("users.dat", 'wb') as f:
            f.write(pickle.dumps(self.users))

    def load_state(self):
        try:
            with open("events.dat", 'rb') as f:
                self.events = pickle.loads(f.read())
        except FileNotFoundError:
            pass

        try:
            with open("users.dat", 'rb') as f:
                self.users = pickle.loads(f.read())
        except FileNotFoundError:
            pass

        if self.events:
            for event in self.events:
                event.print()
        else:
            print(Fore.LIGHTBLUE_EX, "No any planned events")

    async def check_events(self):
        while True:
            await asyncio.sleep(1.)
            for ev in self.events:
                if ev.should_be_cancelled():
                    ev.active = False
                    ev.cancelled = True
                    message = Text.EVENT_CANCELLED.format(Topic=ev.Topic)
                    await bot.send_message(chat_id, message, reply_to_message_id=ev.id, parse_mode=ParseMode.HTML)
                    await bot.unpin_chat_message(chat_id, message_id=ev.id)
                    await self.post_or_edit_event(ev)
                    ev.pending_removal()
                    self.events.remove(ev)
                    self.save_state()
                    continue
                if ev.should_notify():
                    ev.set_notified()
                    message = Text.EVENT_REMIND.format(Topic=ev.Topic, MEMBERS=", ".join(ev.Members), NOTIFY_IN_MINS=NOTIFY_IN_MINS)
                    await bot.send_message(chat_id, message, reply_to_message_id=ev.id, parse_mode=ParseMode.HTML)
                    self.save_state()
                    continue
                if ev.is_already_happened():
                    ev.active = False
                    await self.post_or_edit_event(ev)
                    await bot.unpin_chat_message(chat_id, message_id=ev.id)
                    ev.pending_removal()
                    self.events.remove(ev)
                    self.save_state()
                    continue




    async def handle_message(self, msg: types.Message):
        user_id = msg.from_user.id
        text = msg.text



        if msg.chat.id > 0:

            if msg.text == "/IamYOURhost!!!":
                if msg.from_user.id not in self.users:
                    self.users.append(msg.from_user.id)
                    self.save_state()
                    await msg.answer(f"Okay! Now I serve you :)")
                else:
                    await msg.answer(f"You're already my host. I serve you")
                return

            if msg.from_user.id not in self.users:
                if msg.from_user.id not in self.wrong_users:
                    self.wrong_users.append(msg.from_user.id)
                    await msg.answer(f"Sorry, {msg.from_user.username}, I can't talk with you")
                return

            if text == "/cancel":
                if user_id in self.sessions:
                    if user_id in self.sessions:
                        del self.sessions[user_id]
                        await msg.answer(f"Cancelling event creation")
                    if user_id in self.stop_sessions:
                        del self.stop_sessions[user_id]
                        await msg.answer(f"Cancelling event stop")
                    return

            if text == "/stop":
                await msg.answer(f"You want to stop existing event. '/cancel' to cancel stopping event")
                self.stop_sessions[user_id] = CancelEventSession()
                await msg.answer(f"Please type topic name that you want to stop")
                return

            if user_id in self.stop_sessions:
                cancel_session = self.stop_sessions[user_id]
                await self.handle_event_stop(msg, cancel_session)


            if user_id in self.sessions:
                event = self.sessions[user_id]
                try:
                    await self.handle_event_creation(msg, event)
                except Exception as e:
                    await msg.answer("something went wrong, try again. Or pm to @broly_divine")
                    raise
                return

            if msg.text == "/event":
                await msg.answer(f"You want to create new event. '/cancel' to cancel event creation")
                event = self.sessions[msg.from_user.id] = Event()
                try:
                    await self.handle_event_creation(msg, event)
                except Exception as e:
                    await msg.answer("something went wrong, try again. Or pm to @broly_divine")
                    raise
                return

            if msg.text == "/clear":
                await msg.answer(f"You cleared all events. All events turned to inactive")
                events = self.events

                for event in events:
                    event.active = False
                    event.cancelled = True
                    await self.post_or_edit_event(event)
                    event.pending_removal()
                    self.events.remove(event)
                self.save_state()

                return


            if msg.text.startswith("/invite"):
                text = msg.text.lstrip("/invite").strip()
                nickname = text[0:text.find(" ")]
                topic = text.lstrip(nickname).strip()
                if ev := self.try_find_event_by_topic(topic):
                    if nickname not in ev.Members:
                        ev.add_member(nickname)
                        await self.post_or_edit_event(ev)
                        self.save_state()
                        await msg.answer(f"{nickname} has been invited to '{ev.Topic}' event")
                        await bot.send_message(chat_id, f"@{msg.from_user.username} added {nickname} to  <b>{ev.Topic}</b>", parse_mode=ParseMode.HTML)
                    else:
                        await msg.answer(f"{nickname} already invited to '{ev.Topic}'")
                else:
                    await msg.answer(f"Can't find event with {topic} topic")
                return

            if msg.text.startswith("/kick"):
                text = msg.text.lstrip("/kick").strip()
                nickname = text[0:text.find(" ")]
                topic = text.lstrip(nickname).strip()
                if ev := self.try_find_event_by_topic(topic):
                    if nickname in ev.Members:
                        ev.del_member(nickname)
                        await self.post_or_edit_event(ev)
                        self.save_state()
                        await msg.answer(f"{nickname} has been kicked from event {ev.Topic}")
                        await bot.send_message(chat_id, f"@{msg.from_user.username} removed {nickname} from <b>{ev.Topic}</b>", parse_mode=ParseMode.HTML)
                    else:
                        await msg.answer(f"{nickname} not participates in {ev.Topic}")
                else:
                    await msg.answer(f"Can't find event with {topic} topic")
                return


        else:
            await self.handle_chat_message(msg)

    async def handle_chat_message(self, msg: types.Message):
        text = msg.text
        if text.startswith("+") or text.startswith("-"):
            topic_name = text[1:].strip()
            should_participate = text[0] == "+"
            if ev := self.try_find_event_by_topic(topic_name):
                if msg.from_user.username:
                    name = "@" + msg.from_user.username
                else:
                    name = msg.from_user.first_name
                ev.add_member(name) if should_participate else ev.del_member(name)
                await self.post_or_edit_event(ev)
                self.save_state()

    async def handle_event_stop(self, msg, cancel_session: CancelEventSession):
        if cancel_session.topic_name is None:
            topic_name = msg.text.strip()
            for ev in self.events:
                if ev.Topic == topic_name:
                    cancel_session.topic_name = topic_name
                    cancel_session.event = ev
                    await msg.answer("<code>1/1</code> Please specify deletion reason", parse_mode=ParseMode.HTML)
                    return
            await msg.answer(f"Can't find such topic '{msg.text}'")
        elif cancel_session.reason is None:
            await bot.send_message(chat_id, Text.CANCELLED_BY_REASON.format(TOPIC=cancel_session.event.Topic, REASON=msg.text),
                                        reply_to_message_id=cancel_session.event.id, parse_mode=ParseMode.HTML)
            cancel_session.event.active = False
            cancel_session.event.cancelled = True
            await self.post_or_edit_event(cancel_session.event)
            await bot.unpin_chat_message(chat_id, message_id=cancel_session.event.id)
            del self.stop_sessions[msg.from_user.id]
            self.events.remove(cancel_session.event)
            self.save_state()

    async def handle_event_creation(self, msg, event: Event):
        if event.CreationState == None:
            event.CreationState = 'topic'
            await msg.answer(f"<code>1/7</code> Please specify the topic <b>(one word is better)</b>", parse_mode=ParseMode.HTML)
        elif event.CreationState == 'topic':
            event.Topic = msg.text
            event.CreationState = 'description'
            await msg.answer(f"<code>2/7</code> Topic '{msg.text}' is set. Now set description please", parse_mode=ParseMode.HTML)
        elif event.CreationState == 'description':
            event.Description = msg.text
            event.CreationState = 'date'
            await msg.answer(f"<code>3/7</code> Ok. Description is set. Now set date of event in format <b>18/12/2021 19:30</b>", parse_mode=ParseMode.HTML)
        elif event.CreationState == 'date':
            s = strptime(msg.text, '%d/%m/%Y %H:%M')
            event.Date = datetime.datetime.fromtimestamp(mktime(s))
            event.CreationState = 'levels'
            await msg.answer(f"<code>4/7</code> Ok. Date is set. Now set levels", parse_mode=ParseMode.HTML)
        elif event.CreationState == 'levels':
            event.set_levels(msg.text)
            event.CreationState = 'min_members'
            await msg.answer(f"<code>5/7</code> Ok. Levels are set. Now please set minimum num of participants", parse_mode=ParseMode.HTML)
        elif event.CreationState == 'min_members':
            event.min_members = int(msg.text)
            event.CreationState = 'attach_pic'
            await msg.answer(f"<code>6/7</code> Ok. Min members number is set. Now attach picture to post if you want (or just send NO)", parse_mode=ParseMode.HTML)
        elif event.CreationState == 'attach_pic':
            if msg.photo:
                event.Photo = msg.photo[-1].file_id
            event.CreationState = 'done'
            await msg.answer(f"<code>7/7</code> Ok. Event is created. It will look like here", parse_mode=ParseMode.HTML)

            inline_btn_1 = InlineKeyboardButton(Text.WILL_GO, callback_data=f'+{event.Topic}')
            inline_btn_2 = InlineKeyboardButton(Text.WONT_GO, callback_data=f'-{event.Topic}')
            inline_kb1 = InlineKeyboardMarkup().row(inline_btn_1, inline_btn_2)

            await msg.answer(event.to_text(), parse_mode=ParseMode.HTML, reply_markup=inline_kb1)
            button_yes = KeyboardButton('Yes')
            button_no = KeyboardButton('No')
            ans_kb1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_yes).add(button_no)
            await msg.answer(f"<b>Post this event?</b>", reply_markup=ans_kb1, parse_mode=ParseMode.HTML)
        elif event.CreationState == 'done':
            if msg.text.lower() == 'yes':
                del self.sessions[msg.from_user.id]
                await self.post_or_edit_event(event)
                event.print()
            if msg.text.lower() == 'no':
                del self.sessions[msg.from_user.id]

    async def post_or_edit_event(self, event: Event):

        if event.active:
            inline_btn_1 = InlineKeyboardButton(Text.WILL_GO, callback_data=f'+{event.Topic}')
            inline_btn_2 = InlineKeyboardButton(Text.WONT_GO, callback_data=f'-{event.Topic}')
            inline_kb1 = InlineKeyboardMarkup().row(inline_btn_1, inline_btn_2)
        else:
            inline_kb1 = None

        if event.id is not None:
            if event.Photo:

                await bot.edit_message_caption(chat_id, event.id, caption=event.to_text(), parse_mode=ParseMode.HTML, reply_markup=inline_kb1)
            else:
                await bot.edit_message_text(event.to_text(), chat_id, event.id, parse_mode=ParseMode.HTML, reply_markup=inline_kb1)
            return


        if event.Photo:
            message = await bot.send_photo(chat_id, event.Photo, caption=event.to_text(), parse_mode=ParseMode.HTML, reply_markup=inline_kb1)
        else:
            message = await bot.send_message(chat_id, event.to_text(), parse_mode=ParseMode.HTML, reply_markup=inline_kb1)
        await bot.pin_chat_message(chat_id, message.message_id)
        message_id = message.message_id
        event.id = message_id
        self.events.append(event)
        self.save_state()


    def try_find_event_by_topic(self, topic: str) -> Event:
        for ev in self.events:
            if topic.startswith("1") and not ev.Topic.startswith("1"):
                topic = topic.lstrip("1")
            if ev.Topic.lower() == topic.lower():
                return ev

    async def handle_query(self, callback_query: types.CallbackQuery):
        text = callback_query.data
        if text.startswith("+") or text.startswith("-"):
            topic_name = text[1:].strip()
            should_participate = text[0] == "+"
            if ev := self.try_find_event_by_topic(topic_name):
                if callback_query.from_user.username:
                    name = "@" + callback_query.from_user.username
                else:
                    name = callback_query.from_user.first_name
                if ev.add_member(name) if should_participate else ev.del_member(name):
                    await self.post_or_edit_event(ev)
                    self.save_state()
                await callback_query.answer()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    pass





@dp.message_handler(content_types=['text','photo'])
async def get_text_messages(msg: types.Message):
    await EvRegBot().handle_message(msg)



async def post_event(event: Event, specific_message_id=None):
    global events


@dp.my_chat_member_handler()
async def get_text_chat_messages(msg: types.Message):
    print(msg)


@dp.callback_query_handler()
async def process_callback_button(callback_query: types.CallbackQuery):
    await EvRegBot().handle_query(callback_query)