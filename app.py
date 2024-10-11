from flask import Flask, request, jsonify
from joblib import load
import pandas as pd
import random

app = Flask(__name__)

# Load the pre-trained models (mocked for now)
mlp_model = load('mlp_model.joblib')  # Your existing model
scaler = load('scaler.joblib')  # Your existing scaler

# Define peak hours
peak_hours = [(12, 14), (18, 20)]

def is_peak_hour(hour):
    for start, end in peak_hours:
        if start <= hour < end:
            return True
    return False

def employees_required(day_of_week):
    if day_of_week in ['Saturday', 'Sunday']:
        return 35  # More employees required on weekends
    else:
        return 30  # Normal employees on weekdays

@app.route('/schedule', methods=['POST'])
def generate_schedule():
    data = request.json
    restaurant_id = data['restaurant_id']
    day_of_week = data['day_of_week']
    num_male_employees = data['num_male_employees']
    num_female_employees = data['num_female_employees']
    traffic = random.randint(1, 50)  # Random traffic for the day

    employees = []
    total_employees = num_male_employees + num_female_employees
    required_employees = employees_required(day_of_week)  # Adjust employees based on the day of the week
    shift_hours = [9, 13, 17]  # Fixed shifts for simplicity: 9 AM, 1 PM, 5 PM

    vacant_slots = 0

    for i in range(required_employees):
        if i < num_male_employees:
            emp_type = f"male_emp_{i + 1}"
            shift_start = random.choice(shift_hours)  # Male employees can work any shift
            shift_end = shift_start + 9  # Fixed 9-hour shifts
        elif i < num_male_employees + num_female_employees:
            emp_type = f"female_emp_{i - num_male_employees + 1}"
            shift_start = random.choice([9, 13])  # Female employees can only work shifts that end by 9 PM
            shift_end = min(shift_start + 9, 21)  # Ensuring female employees finish by 9 PM
        else:
            emp_type = "vacant"
            vacant_slots += 1
            shift_start = 9  # Default values for vacant shifts
            shift_end = 18

        workload = traffic / total_employees if total_employees > 0 else 0
        peak_factor = 1.5 if is_peak_hour(shift_start) else 1.0
        
        # Calculate the actual hours worked
        hours_worked = shift_end - shift_start
        
        # Salary calculations
        salary = 0
        for hour in range(shift_start, shift_end):
            if is_peak_hour(hour):
                salary += 15  # 15 rupees during peak hours
            else:
                salary += 10  # 10 rupees during non-peak hours
        
        burnout = workload * peak_factor

        # New satisfaction formula: salary / burnout
        satisfaction = salary / (burnout + 1)  # Avoiding division by zero

        employees.append({
            'employee_id': emp_type,
            'day_of_week': day_of_week,
            'shift': f'{shift_start}:00 - {shift_end}:00',
            'salary': salary,  # Salary based on calculated total
            'burnout': burnout,
            'satisfaction': satisfaction
        })

    # Sort employees by shift first and then by satisfaction in descending order
    employees = sorted(employees, key=lambda x: (x['shift'], x['satisfaction']), reverse=True)

    result = {
        'employees': employees,
        'vacant_slots': vacant_slots,
        'total_required_employees': required_employees
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
