from flask import Flask, request, jsonify
import pandas as pd
import random

import streamlit as st

app = Flask(__name__)

# Load employee data
employee_data = pd.read_csv('restaurant_staff_schedule.csv')

# Constants
FEMALE_END_TIME = 21  # 9 PM
SHIFT_DURATION = 9  # 9-hour shift
PROHIBITED_HOURS = (1, 5)  # No shifts between 1 AM and 5 AM

# Define possible shift start and end times (dynamic allocation)
shift_hours = [(9, 17), (10, 18), (12, 20), (15, 23)]  # Example shifts

def employees_required(day_of_week, avg_traffic):
    # Adjust the number of required employees based on traffic
    if day_of_week in ['Saturday', 'Sunday']:
        return 35 + int(avg_traffic / 10)
    else:
        return 30 + int(avg_traffic / 10)

def filter_employees(restaurant_id, day_of_week):
    # Filter employees by restaurant ID and day of the week
    available_employees = employee_data[(employee_data['restaurant_id'] == restaurant_id) & 
                                        (employee_data['day_of_week'] == day_of_week)]
    print(f"Filtered {len(available_employees)} employees for Restaurant {restaurant_id} on {day_of_week}.")
    return available_employees

@app.route('/predict_demand', methods=['POST'])
def predict_demand():
    try:
        data = request.json
        restaurant_id = data['restaurant_id']
        day_of_week = data['day_of_week']

        # Simulate traffic and sales for the day (replace with real logic if needed)
        predicted_traffic = random.randint(20, 100)
        predicted_sales = random.uniform(2000, 10000)

        # Simulate employee demand based on traffic and sales
        base_employees = 20 if day_of_week in ['Monday', 'Tuesday', 'Wednesday', 'Thursday'] else 30
        additional_employees = int(predicted_sales / 1000) + int(predicted_traffic / 20)
        total_employees_needed = base_employees + additional_employees

        # Simulate a 60% male to 40% female split in the workforce
        predicted_male = int(total_employees_needed * 0.6)
        predicted_female = total_employees_needed - predicted_male

        result = {
            'predicted_male': predicted_male,
            'predicted_female': predicted_female,
            'predicted_traffic': predicted_traffic,
            'predicted_sales': predicted_sales
        }

        return jsonify(result)
    
    except Exception as e:
        print(f"Error predicting demand: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/schedule', methods=['POST'])
def generate_schedule():
    try:
        data = request.json
        restaurant_id = data['restaurant_id']
        day_of_week = data['day_of_week']
        num_male_employees = data['num_male_employees']
        num_female_employees = data['num_female_employees']
        avg_traffic = random.randint(1, 50)  # Random traffic for the day
        predicted_sales = random.uniform(100, 600)  # Predicted sales for the day

        print(f"Received request for Restaurant {restaurant_id} on {day_of_week} with {num_male_employees} male and {num_female_employees} female employees.")

        # Filter available employees
        available_employees = filter_employees(restaurant_id, day_of_week)
        if available_employees.empty:
            raise ValueError("No employees available for the selected restaurant and day.")

        # Separate male and female employees
        male_employees = available_employees[available_employees['gender'] == 'Male'].head(num_male_employees)
        female_employees = available_employees[available_employees['gender'] == 'Female'].head(num_female_employees)

        # Combine male and female employees into one DataFrame
        employees = pd.concat([male_employees, female_employees], ignore_index=True)
        
        total_employees = len(employees)
        required_employees = employees_required(day_of_week, avg_traffic)
        vacant_slots = max(required_employees - total_employees, 0)

        # Assign dynamic shifts to employees
        for i in range(total_employees):
            if employees.at[i, 'gender'] == 'Female':
                # Female employees can't work past 9 PM
                possible_shifts = [shift for shift in shift_hours if shift[1] <= FEMALE_END_TIME]
            else:
                possible_shifts = shift_hours  # Male employees can work any shift
            shift_start, shift_end = random.choice(possible_shifts)
            employees.at[i, 'shift'] = f"{shift_start}:00 - {shift_end}:00"

        # Calculate salary, burnout, and satisfaction dynamically
        employees['salary'] = employees.apply(lambda x: random.randint(90, 110), axis=1)
        employees['burnout'] = employees.apply(lambda x: random.uniform(1.0, 9.0), axis=1)
        employees['satisfaction'] = employees.apply(lambda x: random.uniform(65.0, 90.0), axis=1)

        # Sort employees by satisfaction
        employees = employees.sort_values(by='satisfaction', ascending=False).reset_index(drop=True)

        result = {
            'employees': employees.to_dict(orient='records'),
            'vacant_slots': vacant_slots,
            'total_required_employees': required_employees,
            'predicted_sales': predicted_sales
        }

        return jsonify(result)

    except Exception as e:
        print(f"Error generating schedule: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
