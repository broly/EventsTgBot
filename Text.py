
USE_RUSSIAN = True


class Text:
    """

    ATTENTION!
    Here are text that visible to telegram channel members
    You can edit it as you want, but be sure, the part of text inside {...} braces is special
    the program will substitute this special text automatically from code

    Also, this is HTML-like text
    <b> is bold </b>
    <i> is italic </i>
    <code> is monowide </code>
    \n - is next line

    """

    if USE_RUSSIAN:
        CLOSED = '🔴 <code>ЗАКРЫТО</code>'
        TOOK_PLACE = '✅ ️<code>ЗАВЕРШИЛОСЬ</code>'
        MORE_MEMBERS_NEEDED = '🟣 <code>ТРЕБУЕТСЯ ЕЩЁ {required_people} УЧАСТНИКА</code>'
        WILL_BEGIN_NOW = '🔵 <code>СЕЙЧАС НАЧНЕТСЯ</code>'
        OPEN = '🟢 <code>ОТКРЫТО</code>'

        EVENT_BODY = \
            "{STATUS} \n" \
            "<b>{TOPIC}</b>\n\n" \
            "📅 {DATETIME}\n\n" \
            "<i>{DESCRIPTION}</i>\n\n" \
            "Уровни: {LEVELS}\n" \
            "👤 Нам надо {MIN_MEMBERS}+ участников\n" \
            "👥 Участвуют:\n {PARTY}\n\n" \
            "Чтобы участвовать, напиши: <code>+{TOPIC}</code>\n" \
            "Если передумал: <code>-{TOPIC}</code>\n\n"

        CANCELLED_BY_REASON = "🔴 Событие <b>{TOPIC}</b> отменено\n{REASON}"

        EVENT_CANCELLED = '🔴 К сожалению событие <b>{Topic}</b> отменено. Недостаточно участников 😞'
        EVENT_REMIND = '🟢 Напоминание: событие <b>{Topic}</b> сейчас начнется\n{MEMBERS} ждем вас через {NOTIFY_IN_MINS} минут 😊'

        WILL_GO = "✅ Участвую"
        WONT_GO = "❌ Не участвую"
    else:
        CLOSED = '🔴 <code>CLOSED</code>'
        TOOK_PLACE = '✅ ️<code>TOOK PLACE</code>'
        MORE_MEMBERS_NEEDED = '🟣 <code>{required_people} MORE MEMBERS NEEDED</code>'
        WILL_BEGIN_NOW = '🔵 <code>WILL BEGIN NOW</code>'
        OPEN = '🟢 <code>OPEN</code>'

        EVENT_BODY = \
            "{STATUS} \n" \
            "<b>{TOPIC}</b>\n\n" \
            "📅 {DATETIME}\n\n" \
            "<i>{DESCRIPTION}</i>\n\n" \
            "Levels: {LEVELS}\n" \
            "👤 We need {MIN_MEMBERS}+ members\n" \
            "👥 Party:\n {PARTY}\n\n" \
            "To participate type: <code>+{TOPIC}</code>\n" \
            "To leave: <code>-{TOPIC}</code>\n\n"

        CANCELLED_BY_REASON = "🔴 The event <b>{TOPIC}</b> will not take place\n{REASON}"


        EVENT_CANCELLED = '🔴 Unfortunately the event <b>{Topic}</b> has been cancelled. Not enough participants 😞'
        EVENT_REMIND = '🟢 Remind: an event <b>{Topic}</b> will occur now\n{MEMBERS} waiting for you in {NOTIFY_IN_MINS} mins 😊'

        WILL_GO = "✅ Will go"
        WONT_GO = "❌ Won't go"