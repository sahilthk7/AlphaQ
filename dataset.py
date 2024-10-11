import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker to generate random names
fake = Faker()

# Constraints
restaurant_ids = [1, 2, 3]
genders = ['Male', 'Female']
shift_duration = 9  # 9-hour shift
handover_duration = 1  # 1 hour max
female_end_time = 21  # 9 PM

# Restaurant hours
opening_time = 5  # 5 AM
closing_time = 25  # 1 AM is considered as 25th hour for the next day
peak_hours = [(11, 14), (18, 21)]  # Peak workload and higher sales hours
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Function to generate random shift times
def generate_shift(gender):
    start_hour = random.randint(opening_time, closing_time - shift_duration - handover_duration)
    if gender == 'Female' and start_hour + shift_duration > female_end_time:
        start_hour = random.randint(opening_time, female_end_time - shift_duration)
    
    shift_start = datetime.strptime(f"{start_hour % 24}:00", "%H:%M")  # Wrap to 24-hour format
    shift_end = shift_start + timedelta(hours=shift_duration)
    
    return shift_start.time(), shift_end.time()

# Function to calculate workload based on traffic and employee count
def calculate_workload(traffic, employee_count):
    base_workload = random.uniform(0.3, 0.6) if traffic < 30 else random.uniform(0.6, 1.0)
    return round(base_workload * (50 / employee_count), 2)

# Generate employee dataset
data = []
for i in range(50000):
    employee_id = i + 1
    employee_name = fake.name()
    gender = random.choice(genders)
    satisfaction = random.randint(1, 10)
    burnout = round(10 - satisfaction, 2)
    restaurant_id = random.choice(restaurant_ids)
    shift_start, shift_end = generate_shift(gender)
    day_of_week = random.choice(days_of_week)
    
    avg_traffic = random.randint(1, 50)
    employee_count = random.randint(1, 30)
    workload = calculate_workload(avg_traffic, employee_count)
    
    salary = 10 if workload < 0.5 else 15  # Simplified rule for salary
    avg_sale_per_hour = round(random.uniform(100, 600), 2)  # Random sales per hour

    data.append({
        'employee_id': employee_id,
        'employee_name': employee_name,
        'restaurant_id': restaurant_id,
        'shift_start': shift_start,
        'shift_end': shift_end,
        'gender': gender,
        'workload': workload,
        'employee_satisfaction': satisfaction,
        'burnout': burnout,
        'avg_sale_per_hour': avg_sale_per_hour,
        'day_of_week': day_of_week,
        'avg_traffic': avg_traffic,  # New column for avg traffic
    })

# Convert to DataFrame
df = pd.DataFrame(data)
df.to_csv('restaurant_staff_schedule.csv', index=False)
