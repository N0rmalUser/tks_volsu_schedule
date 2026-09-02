import asyncio

from app.services.schedule import ScheduleService


async def main() -> None:
    service = ScheduleService()
    await service.init_schedule()


if __name__ == "__main__":
    asyncio.run(main())
