import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Function to convert a DataFrame to Excel
def convert_df_to_excel(df, summary_data):
    # Write data to Excel
    with pd.ExcelWriter("MIS_Report.xlsx", engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Shift Schedule', index=False)

        # Create a new worksheet for summary data
        summary_df = pd.DataFrame([summary_data], columns=summary_data.keys())
        summary_df.to_excel(writer, sheet_name='MIS Summary', index=False)

        # Properly close the writer
        writer.close()

    # Read the file to provide it as a download
    with open("MIS_Report.xlsx", "rb") as file:
        return file.read()

# Function to generate a Gantt chart for employee shifts
def generate_gantt_chart(schedule_df):
    # Filter out vacant slots and rows with invalid shifts
    filtered_schedule = schedule_df[schedule_df['employee_name'] != 'Vacant Slot']
    filtered_schedule = filtered_schedule.dropna(subset=['shift'])

    # Convert shift times into proper datetime for Gantt chart
    def parse_shift(shift_str):
        shift_start_str, shift_end_str = shift_str.split(' - ')
        today = datetime.now().strftime("%Y-%m-%d")
        shift_start = datetime.strptime(f"{today} {shift_start_str}", "%Y-%m-%d %H:%M")
        shift_end = datetime.strptime(f"{today} {shift_end_str}", "%Y-%m-%d %H:%M")
        return shift_start, shift_end

    filtered_schedule[['shift_start', 'shift_end']] = filtered_schedule['shift'].apply(parse_shift).apply(pd.Series)

    # Create Gantt chart using Plotly
    fig = px.timeline(filtered_schedule, x_start="shift_start", x_end="shift_end", y="employee_name", color="employee_name", title="Employee Shift Schedule Gantt Chart")
    fig.update_layout(xaxis_title="Shift Time", yaxis_title="Employee", showlegend=False)
    st.plotly_chart(fig)

def convert_df_to_excel(df):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter("MIS_Report.xlsx", engine='xlsxwriter') as writer:
        # Write the DataFrame with employee name and salary to Excel
        df[['employee_name', 'salary']].to_excel(writer, sheet_name='MIS Report', index=False)

        # Get the xlsxwriter workbook and worksheet objects.
        workbook = writer.book
        worksheet = writer.sheets['MIS Report']

        # Calculate the total salary
        total_salary = df['salary'].sum()

        # Write the total salary at the end of the sheet
        worksheet.write(len(df) + 1, 0, 'Total Salary')  # Write 'Total Salary' in the first column
        worksheet.write(len(df) + 1, 1, total_salary)    # Write the total salary value in the second column

        # Close the writer (save the file)
        writer.close()

    # Return the saved Excel file as bytes
    with open("MIS_Report.xlsx", "rb") as file:
        return file.read()

# Function to visualize employee satisfaction levels
def visualize_employee_satisfaction(schedule_df):
    fig = px.bar(schedule_df, x='employee_name', y='satisfaction', color='satisfaction', title="Employee Satisfaction Levels")
    st.plotly_chart(fig)

# Main Streamlit interface
st.title("Restaurant HR Management Dashboard")

# Admin View
if st.selectbox("Login as", ["Admin"], key="login_type_admin") == "Admin":
    st.header("Admin Panel - Generate Shift Schedule")

    restaurant_id = st.selectbox("Select Restaurant ID", [1, 2, 3])
    day_of_week = st.selectbox("Select Day of Week", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    # Initialize state for predicted employees if not already set
    if 'predicted_male' not in st.session_state:
        st.session_state.predicted_male = 5  # Default value
    if 'predicted_female' not in st.session_state:
        st.session_state.predicted_female = 5  # Default value

    if st.button("Predict Employee Demand"):
        # Call the backend API to get predictions
        response = requests.post('http://localhost:5000/predict_demand', 
                                 json={'restaurant_id': restaurant_id, 'day_of_week': day_of_week})

        if response.status_code == 200:
            result = response.json()
            st.session_state.predicted_male = result['predicted_male']
            st.session_state.predicted_female = result['predicted_female']
            
            st.success(f"Predicted: {st.session_state.predicted_male} Male Employees and {st.session_state.predicted_female} Female Employees needed")
            st.info(f"Based on predicted traffic of {result['predicted_traffic']} and sales of ₹{result['predicted_sales']:.2f}")
        else:
            st.error("Error predicting demand. Please try again.")

    # Initialize employee numbers based on prediction (or default)
    num_male_employees = st.number_input("Number of Male Employees", min_value=1, max_value=30, step=1, value=st.session_state.predicted_male)
    num_female_employees = st.number_input("Number of Female Employees", min_value=1, max_value=30, step=1, value=st.session_state.predicted_female)

    if st.button("Generate Schedule"):
        # Call Flask API to generate schedule
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

            # Create a new column for displaying employee names with gender indication
            schedule_df['employee_name'] = schedule_df.apply(lambda row: f"{row['employee_name']} (M)" if row['gender'] == 'Male' else f"{row['employee_name']} (F)", axis=1)

            st.subheader('Shift Schedule')
            # Only display the required columns, excluding shift_start and shift_end
            st.dataframe(schedule_df[['employee_name', 'shift', 'salary', 'burnout', 'satisfaction']])

            st.write(f"Vacant Slots: {result['vacant_slots']}")
            st.write(f"Total Employees Required for the Day: {result['total_required_employees']}")

            # Generate Gantt chart for shifts, excluding vacant slots
            st.subheader("Employee Shift Schedule - Gantt Chart")
            generate_gantt_chart(schedule_df)

            # Visualize employee satisfaction levels
            st.subheader("Employee Satisfaction Levels")
            visualize_employee_satisfaction(schedule_df)

            # Generate simplified MIS Report
            excel_data = convert_df_to_excel(schedule_df)

            # Add download button for the MIS report
            st.download_button(
                label="Download Salary Report",
                data=excel_data,
                file_name=f'Salary_Report_{restaurant_id}_{day_of_week}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )


# Employee View: Check individual schedule
if st.selectbox("Login as", ["Employee"], key="login_type_employee") == "Employee":
    st.header("Employee Dashboard - Check Your Schedule")

    employee_name = st.text_input("Enter your Employee Name")
    day_of_week = st.selectbox("Select Day of Week to Check", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    if st.button("Check My Schedule"):
        response = requests.post('http://localhost:5000/schedule', json={'restaurant_id': 1, 'day_of_week': day_of_week, 'num_male_employees': 10, 'num_female_employees': 10})

        if response.status_code == 200:
            result = response.json()
            schedule_df = pd.DataFrame(result['employees'])

            # Filter to show only the current employee's schedule
            employee_schedule = schedule_df[schedule_df['employee_name'].str.lower() == employee_name.lower()]

            if not employee_schedule.empty:
                st.subheader(f"Schedule for {employee_name} on {day_of_week}")
                st.write(employee_schedule[['shift', 'salary', 'burnout', 'satisfaction']])
            else:
                st.warning(f"No shifts scheduled for {employee_name} on {day_of_week}.")
        else:
            st.error("Error retrieving schedule. Please try again.")
