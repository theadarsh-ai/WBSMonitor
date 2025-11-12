"""
Script to create a sample WBS Excel file for testing.
"""
import pandas as pd
from datetime import datetime, timedelta
import os

def create_sample_wbs():
    """Create a sample WBS Excel file with the specified tasks."""
    
    # Sample data matching the user's requirements
    data = {
        'Task Name': [
            'Client to send completed EIP Master templates',
            'Data validation',
            'EIP database schema design',
            'User authentication setup',
            'L&A Module - Leave approval workflow',
            'L&A Module - Attendance tracking integration',
            'Employee Separation - Exit checklist creation',
            'Employee Separation - Final settlement calculation',
            'C&B - Compensation structure setup',
            'C&B - Benefits enrollment portal',
            'Payroll - Tax calculation engine',
            'Payroll - Salary processing automation',
            'EIP - Employee self-service portal',
            'EIP - Manager dashboard',
            'Integration testing - All modules'
        ],
        'Module': [
            'Employee Information Portal (EIP)',
            'Employee Information Portal (EIP)',
            'Employee Information Portal (EIP)',
            'Employee Information Portal (EIP)',
            'L&A Module',
            'L&A Module',
            'Employee Separation (ES)',
            'Employee Separation (ES)',
            'Compensation & Benefits (C&B)',
            'Compensation & Benefits (C&B)',
            'Payroll & Taxation',
            'Payroll & Taxation',
            'Employee Information Portal (EIP)',
            'Employee Information Portal (EIP)',
            'All Modules'
        ],
        'Mail ID': [
            'adarsh.velmurugan@verint.com',
            'nihar@company.com',
            'dev1@company.com',
            'dev2@company.com',
            'hrteam@company.com',
            'dev3@company.com',
            'hrteam@company.com',
            'finance@company.com',
            'compensation@company.com',
            'benefits@company.com',
            'payroll@company.com',
            'payroll@company.com',
            'dev4@company.com',
            'dev5@company.com',
            'qa@company.com'
        ],
        'Product Owner': [
            'Adarsh Velmurugan',
            'Nihar',
            'Tech Lead',
            'Tech Lead',
            'HR Manager',
            'Tech Lead',
            'HR Manager',
            'Finance Manager',
            'Compensation Manager',
            'Benefits Manager',
            'Payroll Manager',
            'Payroll Manager',
            'Product Manager',
            'Product Manager',
            'QA Manager'
        ],
        'Assigned To': [
            'adarsh.velmurugan@verint.com',
            'nihar@company.com',
            'dev1@company.com',
            'dev2@company.com',
            'hrteam@company.com',
            'dev3@company.com',
            'hrteam@company.com',
            'finance@company.com',
            'compensation@company.com',
            'benefits@company.com',
            'payroll@company.com',
            'payroll@company.com',
            'dev4@company.com',
            'dev5@company.com',
            'qa@company.com'
        ],
        'Duration': [10, 5, 7, 5, 8, 6, 4, 6, 7, 8, 10, 9, 12, 8, 15],
        'Start Date': [],
        'End Date': [],
        'Completion %': [40, 10, 80, 90, 50, 30, 70, 20, 85, 60, 40, 55, 25, 45, 5],
        'Status': [
            'escalation',
            'alert',
            'in progress',
            'in progress',
            'in progress',
            'in progress',
            'in progress',
            'alert',
            'in progress',
            'in progress',
            'in progress',
            'in progress',
            'in progress',
            'in progress',
            'not started'
        ],
        'Dependencies': [
            '',
            '1',
            '',
            '',
            '3',
            '5',
            '4',
            '7',
            '',
            '9',
            '',
            '11',
            '2,3,4',
            '13',
            '5,6,7,8,9,10,11,12,13,14'
        ]
    }
    
    # Calculate dates
    base_date = datetime.now()
    
    for i, duration in enumerate(data['Duration']):
        # Stagger start dates
        start_date = base_date - timedelta(days=duration + (i % 5))
        end_date = start_date + timedelta(days=duration)
        
        # Make first task overdue by 2 days
        if i == 0:
            end_date = base_date - timedelta(days=2)
        
        # Make second task approaching deadline
        if i == 1:
            end_date = base_date + timedelta(days=2)
        
        data['Start Date'].append(start_date)
        data['End Date'].append(end_date)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    output_path = os.path.join('data', 'project_wbs.xlsx')
    os.makedirs('data', exist_ok=True)
    
    df.to_excel(output_path, index=False)
    print(f"✓ Sample WBS file created: {output_path}")
    print(f"  Total tasks: {len(df)}")
    print(f"  Modules: {df['Module'].nunique()}")
    
    return output_path

if __name__ == "__main__":
    create_sample_wbs()
