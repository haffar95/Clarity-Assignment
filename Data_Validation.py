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
    len(invalid_dates)
)

# Calculate percentage of errors
percentage_errors = (rows_with_issues / total_rows) * 100

# HTML report
html_content = f"""
<html>
<head>
    <title>Data Quality Report</title>
    <link rel="stylesheet" type="text/css" href="../CSS/style.css">
</head>
<body>
    <h1>Data Quality Report</h1>
    <div style="text-align: center;">
        <p class="summary">Total Rows in Dataset: <span class="value">{total_rows}</span></p>
        <p class="summary">Rows with Issues: <span class="value">{rows_with_issues}</span> 
        (<span class="value">{percentage_errors:.2f}%</span>)</p>
    </div>

    <h2 style="text-align: center;">Breakdown of Issues</h2>
    <table>
        <tr><th>Issue</th><th>Issue Count</th><th>Rows Number</th></tr>
        <tr><td>Missing Values</td><td class="issue-count">{missing_values_count} </td><td class="row-num">{', '.join(map(str, missing_row_indices))}</td></tr>
        <tr><td>Duplicate Rows</td><td class="issue-count">{duplicate_rows_count} </td><td class="row-num">{', '.join(duplicate_row_indices)}</td></tr>
        <tr><td>Price Outliers</td><td class="issue-count">{len(price_outliers)} </td><td class="row-num">{', '.join(map(str, price_outlier_indices))}</td></tr>
        <tr><td>Quantity Outliers</td><td class="issue-count">{len(quantity_outliers)} </td><td class="row-num">{', '.join(map(str, quantity_outlier_indices))}</td></tr>
        <tr><td>Total Amount Outliers</td><td class="issue-count">{len(total_amount_outliers)} </td><td class="row-num">{', '.join(map(str, total_amount_outlier_indices))}</td></tr>
        <tr><td>Invalid Dates</td><td class="issue-count">{len(invalid_dates)} </td><td class="row-num">{', '.join(map(str, invalid_date_indices))}</td></tr>
    </table>

</body>
</html>
"""

# Save HTML report
with open(report_file_path, 'w') as report:
    report.write(html_content)

# Print report location
print(f"Data quality report saved to: {report_file_path}")