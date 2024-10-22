# це тимчасова реалізація щоб показати як працюють команди
def get_schedule():
    return "1. Пн 10:00-11:00\n2. Вт 14:00-15:00"

def book_lesson(date, time):
    return f"Урок заброньовано на {date} о {time}"

def cancel_lesson(date, time):
    return f"Урок на {date} о {time} скасовано"

def reschedule_lesson(lesson_id, new_date, new_time):
    return f"Урок {lesson_id} перенесено на {new_date} о {new_time}"

def set_reminder(lesson_id, reminder_time):
    return f"Нагадування про урок {lesson_id} встановлено на {reminder_time}"
