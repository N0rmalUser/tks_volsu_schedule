from PIL import Image, ImageDraw, ImageFont
import json_handler
import utils


def get_teacher_image(week: str, day: str, teacher: str):
    week, day = utils.weeks[week], utils.days[day]

    height, width = 550, 660
    font = ImageFont.truetype('images\\font.ttf', 24)
    schedule = json_handler.get_teacher_schedule(week, day, teacher)

    if schedule:
        for item in schedule:
            if len(item['group']) > 10:
                width += 80
                if len(item['group']) > 20:
                    width += 90

    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    x, y = 20, 10
    line_height = 60
    draw.text((x, y), f"{teacher} на {day.upper()} {week}", font=font, fill='black')
    y = y + 50
    if schedule is None:
        draw.text((x, y), "Сегодня нет пар", font=font, fill='black')
    else:
        draw.text((x, y), "Время", font=font, fill='black')
        draw.text((x + 90, y), "Предмет", font=font, fill='black')
        draw.text((x + 440, y), "Ауд.", font=font, fill='black')
        draw.text((x + 530, y), "Группа", font=font, fill='black')
        for item in schedule:
            y += line_height
            draw.text((x, y), item['time'], font=font, fill='black')
            draw.text((x + 90, y), item['subject'], font=font, fill='black')
            draw.text((x + 440, y), item['room'], font=font, fill='black')
            draw.text((x + 530, y), item['group'], font=font, fill='black')

    image.save('images\\teacher_schedule.png')


def get_room_image(week: str, day: str, room: str):
    week, day, room = utils.weeks[week], utils.days[day], utils.rooms[room]

    height, width = 550, 760
    font = ImageFont.truetype('images\\font.ttf', 24)
    schedule = json_handler.get_room_schedule(room, week, day)

    if schedule:
        for item in schedule:
            if len(item['group']) > 10:
                width += 80
                if len(item['group']) > 20:
                    width += 100

    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    x, y = 20, 10
    line_height = 60
    draw.text((x, y), f"{room} на {day.upper()} {week}", font=font, fill='black')
    y = y + 50
    if schedule is None:
        draw.text((x, y), "Сегодня нет пар", font=font, fill='black')
    else:
        draw.text((x, y), "Время", font=font, fill='black')
        draw.text((x + 90, y), "Предмет", font=font, fill='black')
        draw.text((x + 440, y), "Преподаватель", font=font, fill='black')
        draw.text((x + 650, y), "Группа", font=font, fill='black')
        for item in schedule:
            y += line_height
            draw.text((x, y), item['time'], font=font, fill='black')
            draw.text((x + 90, y), item['subject'], font=font, fill='black')
            draw.text((x + 440, y), item['teacher'], font=font, fill='black')
            draw.text((x + 630, y), item['group'], font=font, fill='black')
    image.save('images\\room_schedule.png')


def get_group_image(week: str, day: str, group: str):
    week, day = utils.weeks[week], utils.days[day]

    height, width = 550, 740
    font = ImageFont.truetype('images\\font.ttf', 24)
    schedule = json_handler.get_group_schedule(group, week, day)

    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    x, y = 20, 10
    line_height = 60
    draw.text((x, y), f"{group} на {day.upper()} {week}", font=font, fill='black')
    y = y + 50
    if schedule is None:
        draw.text((x, y), "Сегодня нет пар", font=font, fill='black')
    else:
        draw.text((x, y), "Время", font=font, fill='black')
        draw.text((x + 90, y), "Предмет", font=font, fill='black')
        draw.text((x + 440, y), "Ауд.", font=font, fill='black')
        draw.text((x + 530, y), "Преподаватель", font=font, fill='black')
        for item in schedule:
            y += line_height
            draw.text((x, y), item['time'], font=font, fill='black')
            draw.text((x + 90, y), item['subject'], font=font, fill='black')
            draw.text((x + 440, y), item['room'], font=font, fill='black')
            draw.text((x + 530, y), item['teacher'], font=font, fill='black')

    image.save('images\\group_schedule.png')
