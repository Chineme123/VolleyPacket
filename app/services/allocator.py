import random
import pandas as pd

SLOTS_PER_DAY = 4
NUM_HALLS = 1
CAPACITY_PER_SLOT = 500
FIRST_SLOT_HOUR = 7
EXAM_DURATION_HRS = 2
BREAK_DURATION_HRS = 0


def format_hour(hour):
    h = int(hour)
    m = int((hour - h) * 60)
    suffix = "AM" if h < 12 else "PM"
    h = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
    return f"{h}:{m:02d} {suffix}"


def generate_combination_slots():
    combination_slots = []
    for slot in range(SLOTS_PER_DAY):
        start_hour = FIRST_SLOT_HOUR + slot * (EXAM_DURATION_HRS + BREAK_DURATION_HRS)
        for hall in range(NUM_HALLS):
            combination_slots.append((f"{format_hour(start_hour)}", f"Hall {hall + 1}"))
    return combination_slots


def allocate_combinations(data, combination_pool):
    for _, group in data.groupby('ExamDate'):
        if len(group) > len(combination_pool):
            continue

        pool_copy = combination_pool.copy()
        random.shuffle(pool_copy)
        daily_pool = pool_copy[:len(group)]

        data.loc[group.index, 'ExamTime'] = [slot[0] for slot in daily_pool]
        data.loc[group.index, 'AssignedHall'] = [slot[1] for slot in daily_pool]
    return data


def assign_numbers(data):
    data = data.sort_values(['ExamDate', 'ExamTime', 'AssignedHall', 'Name'])
    data['Number'] = data.groupby(['ExamDate', 'ExamTime', 'AssignedHall']).cumcount() + 1
    return data
