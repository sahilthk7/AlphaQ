import streamlit as st
import requests
import pandas as pd

# Streamlit interface
st.title('Restaurant Shift Scheduling Optimization')

restaurant_id = st.selectbox('Select Restaurant ID', [1, 2, 3])
day_of_week = st.selectbox('Select Day of Week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
num_male_employees = st.number_input('Number of Male Employees', min_value=1, max_value=30, step=1)
num_female_employees = st.number_input('Number of Female Employees', min_value=1, max_value=30, step=1)

if st.button('Generate Schedule'):
    data = {
        'restaurant_id': restaurant_id,
        'day_of_week': day_of_week,
        'num_male_employees': num_male_employees,
        'num_female_employees': num_female_employees
    }

    response = requests.post('http://localhost:5000/schedule', json=data)
    
    if response.status_code == 200:
        result = response.json()
        schedule_df = pd.DataFrame(result['employees'])

        st.subheader('Shift Schedule (Sorted by Employee Satisfaction)')
        st.dataframe(schedule_df)

        # Display vacant slots and total employees required
        vacant_slots = result['vacant_slots']
        total_required = result['total_required_employees']

        st.write(f"**Vacant Slots**: {vacant_slots}")
        st.write(f"**Total Employees Required for the Day**: {total_required}")
    else:
        st.error('Error generating schedule. Please try again.')
