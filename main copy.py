import csv

def filter_us_states(csv_file_path, output_file_path):
    us_territory_codes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'PR', 'GU', 'VI', 'AS', 'MP']
    po_box_variations = ['PO Box', 'P.O. Box', 'P O Box', 'Post Office Box', 'Post Office']

    with open(csv_file_path, 'r', encoding='utf-8') as input_file, open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames
        print(fieldnames)

        # Write header to the output file
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        # Filter rows and write to the output file
        for row in reader:
            state_column = row.get('PERSONAL_STATE', '')  # Assuming the column name is 'PERSONAL_STATE'
            address_column = row.get('PERSONAL_ADDRESS', '')  # Assuming the column name is 'PERSONAL_ADDRESS'

            # Check conditions before adding the row to the output file
            if state_column in us_territory_codes and address_column and not any(variation in address_column for variation in po_box_variations):
                writer.writerow(row)

# Replace 'your_input_file.csv' and 'output_filtered_states.csv' with the actual paths
input_file_path = 'docs/Adpromoter_FirstPriority.csv'
output_file_path = 'output/output_filtered_states.csv'

filter_us_states(input_file_path, output_file_path)
