import csv

def filter_us_states(csv_file_path, output_file_path):
    us_territory_codes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'PR', 'GU', 'VI', 'AS', 'MP']
    po_box_variations = ['PO Box', 'P.O. Box', 'P O Box', 'Post Office Box', 'Post Office', 'Po Box']

    with open(csv_file_path, 'r', encoding='utf-8') as input_file, open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
        reader = csv.DictReader(input_file)

        # Define the columns for the output file
        output_fieldnames = [
            'Client Customer ID', 'First Name', 'Last Name', 'Street Address 1', 'Street Address 2',
            'City', 'State', 'Zip Code', 'Zip Code Plus 4', 'Email1', 'Email2', 'Email3',
            'PhoneNumber1', 'PhoneNumber2'
        ]

        # Write header to the output file
        writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
        writer.writeheader()

        # Autoincrement for "Client Customer ID"
        client_customer_id_counter = 1

        # Filter rows and write to the output file
        for row in reader:
            state_column = row.get('PERSONAL_STATE', '')  # Assuming the column name is 'PERSONAL_STATE'
            address_column = row.get('PERSONAL_ADDRESS', '')  # Assuming the column name is 'PERSONAL_ADDRESS'

            # Check conditions before adding the row to the output file
            if state_column in us_territory_codes and address_column and not any(variation in address_column for variation in po_box_variations):
                # Prepare the row for the output file
                output_row = {
                    'Client Customer ID': client_customer_id_counter,
                    'First Name': row.get('FIRST_NAME', ''),
                    'Last Name': row.get('LAST_NAME', ''),
                    'Street Address 1': row.get('PERSONAL_ADDRESS', ''),
                    'Street Address 2': row.get('PERSONAL_ADDRESS_2', ''),
                    'City': row.get('PERSONAL_CITY', ''),
                    'State': state_column,
                    'Zip Code': row.get('PERSONAL_ZIP', ''),
                    'Zip Code Plus 4': row.get('PERSONAL_ZIP4', ''),
                    'Email1': row.get('PERSONAL_EMAIL', ''),
                    'Email2': row.get('BUSINESS_EMAIL', ''),
                    'Email3': row.get('BUSINESS_EMAIL', ''),  # Assuming Email3 is from BUSINESS_EMAIL
                    'PhoneNumber1': row.get('DIRECT_NUMBER', ''),
                    'PhoneNumber2': row.get('MOBILE_PHONE', '')
                }

                # Write the row to the output file
                writer.writerow(output_row)

                # Increment the "Client Customer ID" counter
                client_customer_id_counter += 1

# Replace 'your_input_file.csv' and 'output_filtered_states.csv' with the actual paths
input_file_path = 'docs/Adpromoter_FirstPriority.csv'
output_file_path = 'output/output_filtered_states.csv'

filter_us_states(input_file_path, output_file_path)
