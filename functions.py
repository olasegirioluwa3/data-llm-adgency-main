import os
import glob
import pandas as pd

def validate_email(value):
    # po_box_variations = ['PO Box', 'P.O. Box', 'P O Box', 'Post Office Box', 'Post Office']
    valid_email_variations = [
        'Valid (Digital)', 'Valid (Esp)'
    ]


    if  (value in valid_email_variations and value != "-" and value != ""):
        return value

    return None


def programmatic_email_filter(value):
    # check if value is array
        
    # if  (value in valid_email_variations and value != "-" and value != ""):
    #     return value

    return None


def validate_address(*address_fields):
    # po_box_variations = ['PO Box', 'P.O. Box', 'P O Box', 'Post Office Box', 'Post Office']
    po_box_variations = [
        'PO Box', 'P.O. Box', 'P.O Box', 'P.OBOX', 'P O Box', 'Post Office Box', 'po box', 'Po Box', 'PO. Box', 'Post Office', 'Box No', 'Box #', 'Mailbox', 'Mail Box', 'MB',
        'Drawer', 'Drawer No', 'Drawer #', 'Private Bag', 'PMB', 'Postal Bag',
        'Parcel Locker', 'Locker No', 'Locker #', 'Community Mail Center',
        'CMC', 'Apt #', 'Attention', 'Attn', 'Attn:', 'C/O', 'Care Of', 'CO', 'c/o'
    ]


    for address in address_fields:
        if address and not any(variation in address for variation in po_box_variations) and address != "-" and address != "":
            return address

    return None


def check_primary_industry(primary_industry_field):
    valid_industry = [
        'advertising', 'media', 'public relations', 'marketing', 'broadcast', 
        'printing', 'press', 'publishing', 'entertainment', 'event', 
        'Advertising', 'Media', 'Public Relations', 'Marketing', 'Broadcast', 
        'Printing', 'Press', 'Publishing', 'Entertainment', 'Event',
        'ADVERTISING', 'MEDIA', 'PUBLIC RELATIONS', 'MARKETING', 'BROADCAST', 
        'PRINTING', 'PRESS', 'PUBLISHING', 'ENTERTAINMENT', 'EVENT',
        'AdVeRtIsInG', 'MeDiA', 'PuBlIc ReLaTiOnS', 'MaRkEtInG', 'BrOaDcAsT', 
        'PrInTiNg', 'PrEsS', 'PuBlIsHiNg', 'EnTeRtAiNmEnT', 'EvEnT', 'Newspaper'
    ]

    # Check if any valid industry keyword appears in the primary industry field
    for keyword in valid_industry:
        if keyword.lower() in primary_industry_field.lower():
            return True

    return False


# def merge_csv_files(folder_path, output_file):
#     # Check if the output directory exists, create it if not
#     if not os.path.exists(folder_path):
#         print(f"Error: Folder '{folder_path}' not found.")
#         return

#     # Get all CSV files in the specified folder
#     csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

#     if not csv_files:
#         print(f"No CSV files found in '{folder_path}'.")
#         return

#     # Initialize an empty DataFrame to store the merged data
#     merged_data = pd.DataFrame()

#     # Iterate through each CSV file and merge into the DataFrame
#     for csv_file in csv_files:
#         file_path = os.path.join(folder_path, csv_file)
#         try:
#             # Read CSV file into a DataFrame
#             current_data = pd.read_csv(file_path)
#             # Merge the current DataFrame with the existing merged_data
#             merged_data = pd.concat([merged_data, current_data], ignore_index=True, sort=False)
#         except pd.errors.EmptyDataError:
#             print(f"Warning: Empty CSV file found at '{file_path}'.")

#     # Check if 'Email1' is not unique, then group and concatenate the data
#     if merged_data['Email1'].duplicated().any():
        
#         grouped_data = merged_data.groupby('Email1').agg(lambda x: ', '.join(x.astype(str))).reset_index()
#         merged_data = grouped_data

#     # Write the merged DataFrame to a new CSV file
#     merged_data.to_csv(output_file, index=False)
#     print(f"Merged data saved to '{output_file}'.")

#Second version of merge csv
def merge_csv_files2(folder_path, output_file, columns_to_check=None):
    """
    Merges all CSV files in a specified folder into a single CSV file, checks for and drops duplicates 
    in specified columns, and then saves the merged file to an output folder.

    Args:
        folder_path (str): The path to the folder containing CSV files.
        output_file (str): The file path for the output merged CSV file.
        columns_to_check (list of str, optional): The columns to check for duplicates.

    Raises:
        FileNotFoundError: If the specified folder does not exist.
        ValueError: If no CSV files are found in the folder.

    Use Case:
    To merge all CSV files from the folder 'data/csv_files', drop duplicates based on 'Email' and 'UserID' columns,
    and save the result to 'data/merged_output.csv', use:
    >>> merge_csv_files('data/csv_files', 'data/merged_output.csv', ['Email', 'UserID'])
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' not found.")

    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    if not csv_files:
        raise ValueError(f"No CSV files found in '{folder_path}'.")

    duplicates_removed = False  # Flag to track if any duplicates were removed

    try:
        data_frames = [pd.read_csv(file) for file in csv_files]
        merged_data = pd.concat(data_frames, ignore_index=True, sort=False)

        if columns_to_check and merged_data.duplicated(subset=columns_to_check).any():
            merged_data.drop_duplicates(subset=columns_to_check, inplace=True)
            duplicates_removed = True

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        merged_data.to_csv(output_file, index=False)
        duplicates_msg = " and duplicates removed" if duplicates_removed else " with no duplicates"
        print(f"Merged data saved to '{output_file}'{duplicates_msg}.")
    except Exception as e:
        raise Exception(f"An error occurred during processing: {e}")
    

#Slit columns values based on seperator
    
def split_columns_by_separator(df, columns, separator=","):
    """
    Splits the values in specified columns of a DataFrame separated by a given separator into distinct columns.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        columns (list of str): The names of the columns to split. Can be a single column name or a list of names.
        separator (str): The separator used to split the column values.

    Returns:
        pd.DataFrame: A DataFrame with the original columns split into multiple columns.

    Each new column is named based on the original column name with a suffix attached.
    """
    # Ensure columns is a list, even if a single column name is provided
    if isinstance(columns, str):
        columns = [columns]

    # Iterate through each column to be split
    for column in columns:
        # Split the column on the separator and expand to separate columns
        split_columns = df[column].str.split(separator, expand=True)

        # Create new column names
        new_columns = [f"{column}_{i+1}" for i in range(split_columns.shape[1])]

        # Rename the columns
        split_columns.columns = new_columns

        # Concatenate with the original DataFrame
        df = pd.concat([df, split_columns], axis=1)

    return df 
