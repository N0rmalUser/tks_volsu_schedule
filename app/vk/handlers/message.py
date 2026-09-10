import structlog
from vkbottle.bot import BotLabeler, Message

from app.common.utils import get_schedule, get_today
from app.database.session import session_scope
from app.schemas.enums import Keyboard, Platform, UserRole
from app.services.user import UserService
from app.vk.markups import days, directions, group_menu, rooms, teacher_menu, teachers


router = BotLabeler()
log = structlog.get_logger()


@router.message(text=["/start", "Начать"])
async def start_handler(msg: Message):
    log.info("command.start")
    async with session_scope() as session:
        service = await UserService.create(session, Platform.VK, msg.from_id)
        role = await service.get_user_role()
        if role == UserRole.TEACHER:
            menu = teacher_menu()
            keyboard = teachers()
        else:
            menu = group_menu()
            keyboard = directions()
    await msg.answer(
        message="Привет!\n",
        keyboard=menu,
    )
    await msg.answer(
        message="Выбери себя:",
        keyboard=keyboard,
    )


@router.message(command="help")
async def help_handler(msg: Message):
    log.info("command.help")
    await msg.answer(
        """
Привет, это бот расписания кафедры ТКС в вк!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранного преподавателя.
Кнопки `Группы`, `Преподаватели`, `Кабинеты` открывают соответствующие меню выбора.
Из-за ограничения в 10 кнопок, у списка преподавателей добавлены страницы, а у списка групп - разделение по направлениям

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️
""",
    )


@router.message(text="Расписание на сегодня")
async def schedule_handler(msg: Message):
    async with session_scope() as session:
        service = await UserService.create(session, Platform.VK, msg.from_id)
        role: UserRole = await service.get_user_role()

        day, week = get_today()
        entity_id = await service.get_default_id()

    if not entity_id:
        await msg.answer(
            f"Сначала выберите {'ФИО преподавателя' if role == UserRole.TEACHER else 'группу'}, "
            f"нажав на соответствующую кнопку.",
            keyboard=teachers() if role == UserRole.TEACHER else directions(),
        )
        return

    log.info(
        "schedule.view",
        target=role,
        target_id=entity_id,
        week=week,
        day=day,
    )

    if role == UserRole.TEACHER:
        keyboard = Keyboard.TEACHER
        week_kb = days(keyboard_type=keyboard, week=week, day=day, value=entity_id)
    else:
        keyboard = Keyboard.STUDENT
        week_kb = days(keyboard_type=keyboard, week=week, day=day, value=entity_id)

    await msg.answer(
        await get_schedule(
            target=keyboard,
            day=day,
            week=week,
            value=entity_id,
        ),
        keyboard=week_kb,
    )


@router.message(text="Кабинеты")
async def rooms_handler(msg: Message):
    await msg.answer("Выберите кабинет", keyboard=rooms())


@router.message(text="Группы")
async def groups_handler(msg: Message) -> None:
    await msg.answer("Выберите группу", keyboard=directions())


@router.message(text="Преподаватели")
async def teachers_handler(msg: Message) -> None:
    await msg.answer("Выберите преподавателя", keyboard=teachers())
