import pandas as pd
from datetime import datetime
import os

# paths
project_path = r'C:\Users\osama\Desktop\Clarity Assignment'
input_file_path = os.path.join(project_path, 'ecommerce-dataset.csv')
output_directory = os.path.join(project_path, 'output')
report_file_path = os.path.join(output_directory, 'data_quality_report.html')

# output directory
os.makedirs(output_directory, exist_ok=True)

# Load dataset
data = pd.read_csv(input_file_path)

# variables
total_rows = data.shape[0]
missing_values_count = 0
duplicate_rows_count = 0

# Missing Values
missing_values = data.isnull().sum()
missing_rows = data[data.isnull().any(axis=1)]
missing_values_count = len(missing_rows)
missing_row_indices = (missing_rows.index + 2).tolist()

# Duplicates
# Find duplicate based on OrderID as a primary key
duplicates = data[data.duplicated(subset=['OrderID'], keep=False)]
duplicates_grouped = duplicates.groupby('OrderID')
duplicate_row_indices = []
for order_id, group in duplicates_grouped:
    rows = (group.index + 2).tolist()
    duplicate_row_indices.append(f"{{{' ,'.join(map(str, rows))}}}")
duplicate_rows_count = len(duplicate_row_indices)

# Unrealistic Values (Price and Quantity Outliers)
price_outliers = data[(data['Price'] < 0) | (data['Price'] > 10000)]
quantity_outliers = data[(data['Quantity'] <= 0) | (data['Quantity'] > 100)]
price_outlier_indices = (price_outliers.index + 2).tolist()
quantity_outlier_indices = (quantity_outliers.index + 2).tolist()

# Total Amount Outliers (Price * Quantity should match Total Amount)
data['CalculatedTotalAmount'] = data['Price'] * data['Quantity']
total_amount_outliers = data[data['TotalAmount'] != data['CalculatedTotalAmount']]
total_amount_outlier_indices = (total_amount_outliers.index + 2).tolist()

# Date Issues
data['OrderDate'] = pd.to_datetime(data['OrderDate'], errors='coerce')
invalid_dates = data[data['OrderDate'].isnull()]
invalid_date_indices = (invalid_dates.index + 2).tolist()

# Calculate total rows with issues
rows_with_issues = (
    len(missing_rows) +
    len(duplicates) +
    len(price_outliers) +
    len(quantity_outliers) +
    len(invalid_dates) +
    len(total_amount_outliers)
)

# Calculate percentage of errors
percentage_errors = (rows_with_issues / total_rows) * 100

# HTML report
html_content = f"""
<html>
<head>
    <title>Data Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 8px 12px; text-align: left; border: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Data Quality Report</h1>
    <p><strong>Total Rows in Dataset:</strong> {total_rows}</p>
    <p><strong>Rows with Issues:</strong> {rows_with_issues} ({percentage_errors:.2f}%)</p>
    <h2>Breakdown of Issues</h2>
    <table>
        <tr><th>Issue</th><th>Count</th><th>Row Numbers</th></tr>
        <tr><td>Missing Values</td><td>{missing_values_count} rows</td><td>{', '.join(map(str, missing_row_indices))}</td></tr>
        <tr><td>Duplicate Rows</td><td>{duplicate_rows_count} rows</td><td>{', '.join(duplicate_row_indices)}</td></tr>
        <tr><td>Price Outliers</td><td>{len(price_outliers)} rows</td><td>{', '.join(map(str, price_outlier_indices))}</td></tr>
        <tr><td>Quantity Outliers</td><td>{len(quantity_outliers)} rows</td><td>{', '.join(map(str, quantity_outlier_indices))}</td></tr>
        <tr><td>Total Amount Outliers</td><td>{len(total_amount_outliers)} rows</td><td>{', '.join(map(str, total_amount_outlier_indices))}</td></tr>
        <tr><td>Invalid Dates</td><td>{len(invalid_dates)} rows</td><td>{', '.join(map(str, invalid_date_indices))}</td></tr>
    </table>
</body>
</html>
"""

# Save HTML report
with open(report_file_path, 'w') as report:
    report.write(html_content)

# Print report location
print(f"Data quality report saved to: {report_file_path}")
