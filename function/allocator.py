# --- IMPORT ---
import random
import pandas as pd
from read_data import load_data

# --- CONFIG ---
SLOTS_PER_DAY = 3
NUM_HALLS = 2
CAPACITY_PER_SLOT = 50
FIRST_SLOT_HOUR = 8
EXAM_DURATION_HRS = 2
BREAK_DURATION_HRS = 1

# --- HELPERS ---
def format_hour(hour):
    if hour == 24 or hour == 0:
        suffix = "AM"
        hour = 12
    elif hour >= 12:
        suffix = "PM"
        hour = hour - 12 if hour > 12 else hour
    else:
        suffix = "AM"
    return f"{hour}:00 {suffix}"

# --- COMBINATION LOGIC ---
def generate_combination_slots():
    combination_slots = []

    for slot in range(SLOTS_PER_DAY):
        start_hour = FIRST_SLOT_HOUR + slot * (EXAM_DURATION_HRS + BREAK_DURATION_HRS)
        end_hour = start_hour + EXAM_DURATION_HRS
        #print(f"Slot {slot + 1}: {format_hour(start_hour)} - {format_hour(end_hour)}")

        for hall in range(NUM_HALLS):
            #print(f"  Hall {hall + 1}: Capacity {CAPACITY_PER_SLOT}")
            combination_slots.append((f"{format_hour(start_hour)} - {format_hour(end_hour)}", f"Hall {hall + 1}"))

    return combination_slots


# --- CORE LOGIC ---
def allocate_combinations(data, combination_pool):
    for date, group in data.groupby('ExamDate'):
        if len(group) > len(combination_pool):
            print(f"  Warning: Not enough slots for {len(group)} students! Only {len(combination_pool)} slots available.")
            continue

        random.shuffle(combination_pool)
        daily_pool = combination_pool[:len(group)]

        data.loc[group.index, 'ExamTime'] = [slot[0] for slot in daily_pool]
        data.loc[group.index, 'AssignedHall'] = [slot[1] for slot in daily_pool]
    return data

if __name__ == "__main__":
    data = load_data('./data/volley_packet_test_data.xlsx')
    combination_pool = generate_combination_slots() * CAPACITY_PER_SLOT
    allocated_data = allocate_combinations(data, combination_pool)
    #print(allocated_data.head())
    allocated_data.to_excel('./data/allocated_exam_schedule.xlsx', index=False)