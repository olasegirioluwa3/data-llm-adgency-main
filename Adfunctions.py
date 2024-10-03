'''
Addfunction is a package that contains list of functions that are used in creating Advert list given 
particular conditions the list will continue to grow based on the requirements given for the Ads list

'''
#>>>>>>>>>>>>> Import required Packages >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import pandas as pd
import numpy as np
from openpyxl import Workbook
import os
import glob
import re
import random

#>>>>>>>>>>>>> - Define Function to read Data - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_data(file_path, **kwargs):
    """
    Reads data from a CSV file into a pandas DataFrame.

    This function reads a CSV file from the given file path using pandas, allowing additional
    optional parameters to be passed to pandas.read_csv for more flexibility.

    Parameters:
    file_path (str): The file path to the CSV file to be read.
    **kwargs: Optional keyword arguments that are passed to pandas.read_csv.

    Returns:
    pd.DataFrame: A DataFrame containing the data from the CSV file.

    Raises:
    ValueError: If the file_path is not a string.
    FileNotFoundError: If the file does not exist at the specified path.
    Exception: For other issues that may arise during file reading.

    Example:
    >>> df = get_data("path/to/your/data.csv", sep=';', header=None)
    """
    if not isinstance(file_path, str):
        raise ValueError("File path must be a string")

    try:
        df = pd.read_csv(file_path, low_memory=False, **kwargs)
        return df
    except FileNotFoundError:
        raise FileNotFoundError("File not found at the specified path")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")

#>>>>>>>>>> Define Function fcount duplicates >>>>>>>>>>>>>>
    
def count_duplicates(df):
    """
    Checks for duplicate rows in a DataFrame and returns a message indicating the number of duplicates.

    Args:
        df (pd.DataFrame): The DataFrame to check for duplicates.

    Returns:
        str: A message indicating no duplicates or the number of duplicate rows.
    """
    num_duplicates = df.duplicated().sum()

    if num_duplicates == 0:
        return "No duplicates found."
    else:
        return f"The data has {num_duplicates} duplicates."
 
    
#>>>>>>>>>> Define Function filter by sic code >>>>>>>>>>>>>>
def filter_by_sic_codes(df, target_sic_codes):
    """
    Filters a DataFrame to include only rows where at least one SIC code in the 'COMPANY_SIC' field
    matches one of the target SIC codes. Assumes multiple SIC codes in 'COMPANY_SIC' are separated by a delimiter.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    target_sic_codes (list): List of target SIC codes.

    Returns:
    pd.DataFrame: The filtered DataFrame.

    Use Case:
    To filter a DataFrame 'df' to include only rows where the 'COMPANY_SIC' field contains either '1234' or '5678', use:
    >>> df = pd.DataFrame({'COMPANY_SIC': ['1234,2345', '5678,6789', '3456']})
    >>> target_sic_codes = ['1234', '5678']
    >>> filtered_df = filter_by_sic_codes(df, target_sic_codes)
    This will return a DataFrame including only the first two rows where 'COMPANY_SIC' matches '1234' or '5678'.
     DataFrame.
    """
    if 'COMPANY_SIC' not in df.columns:
        raise ValueError("DataFrame must contain a 'COMPANY_SIC' column")

    def contains_target_sic(sic_codes):
        # Split the SIC codes based on the delimiter and check for matches
        sic_list = sic_codes.split(';')  # Adjust the delimiter if necessary
        return any(sic.strip() in target_sic_codes for sic in sic_list)

    # Apply the function to filter the DataFrame
    filtered_df = df[df['COMPANY_SIC'].apply(contains_target_sic)]

    return filtered_df


#>>>>>>>>>> - Define Function "filter_by_seniority" - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def filter_by_seniority(df, exclude_levels=None):
    """
    Filters a dataframe to exclude rows with specified seniority levels in SENIORITY_LEVEL, and rows with non-standard characters in this column.

    Parameters:
    df (pd.DataFrame): DataFrame with a column named "SENIORITY_LEVEL".
    exclude_levels (list, optional): List of seniority levels to exclude, e.g., ["Staff", "Manager"]. Defaults to None.

    Returns:
    pd.DataFrame: DataFrame with rows containing specified levels and non-standard characters removed.

    Raises:
    ValueError: If the DataFrame does not contain a 'SENIORITY_LEVEL' column.
    """
    if 'SENIORITY_LEVEL' not in df.columns:
        raise ValueError("DataFrame must contain a 'SENIORITY_LEVEL' column")

    exclude_levels = [level.lower() for level in (exclude_levels or [])]  # Normalize exclude_levels to lower case
    seniority_regex = re.compile(r"[^\w\s]+")  # Matches non-alphanumeric characters except spaces and underscore

    filtered_df = df[
        df["SENIORITY_LEVEL"].notna() &
        ~df["SENIORITY_LEVEL"].str.lower().isin(exclude_levels) &
        ~df["SENIORITY_LEVEL"].str.contains(seniority_regex)
    ]

    return filtered_df 


#>>>>>>>>>> - Define Function filter_by_valid_business_email - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def filter_by_valid_business_email(df, column_name="BUSINESS_EMAIL_VALIDATION_STATUS"):
    """
    Filters a DataFrame for rows with "Valid" in the specified email validation status column.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    column_name (str): The name of the column containing email validation status. 
                       Defaults to "BUSINESS_EMAIL_VALIDATION_STATUS".

    Returns:
    pd.DataFrame: A new DataFrame containing only rows with validated emails.

    Raises:
    ValueError: If the specified column does not exist in the DataFrame.

    Use Case:
    To filter a DataFrame 'df' to include only rows where the business email validation status is 'Valid', use the function as follows:
    >>> df = pd.read_csv('your_file.csv')
    >>> valid_email_df = filter_by_valid_business_email(df)
    
    If the email validation status is in a different column, specify the column name:
    >>> valid_email_df = filter_by_valid_business_email(df, 'CUSTOM_EMAIL_STATUS_COLUMN')
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    # Filter the DataFrame for rows where the specified column contains 'Valid' (case-insensitive)
    filtered_df = df[df[column_name].str.contains("Valid", case=False, na=False)]

    return filtered_df


#>>>>>>>>>> - Create Function enrich_phone_numbers- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def enrich_phone_numbers(df):
    """
    Enriches phone numbers in a DataFrame by consolidating two phone number columns ('MOBILE_PHONE' and 'DIRECT_NUMBER').
    It replaces '-' with NaN, then creates a new 'ENRICHED_PHONE_NUMBER' column filled with the most complete data 
    available between the two columns, and drops rows where no valid phone number is available.

    Parameters:
    df (pd.DataFrame): The DataFrame with phone number columns.

    Returns:
    pd.DataFrame: A new DataFrame with an 'ENRICHED_PHONE_NUMBER' column, with rows containing NaNs in this column dropped.

    Raises:
    ValueError: If the required phone number columns are not present in the DataFrame.

    Use Case:
    Suppose you have a DataFrame 'df' with two columns 'MOBILE_PHONE' and 'DIRECT_NUMBER', each containing phone numbers.
    Some entries may have missing or invalid numbers represented by '-'. To create a new column 'ENRICHED_PHONE_NUMBER' that
    contains the most reliable phone number available (either mobile or direct), and to remove rows without any valid phone 
    number, use the function as follows:
    >>> df = pd.read_csv('your_file.csv')
    >>> enriched_df = enrich_phone_numbers(df)
    """
    phone_columns = ["MOBILE_PHONE", "DIRECT_NUMBER"]

    # Check if the required columns are present
    if not set(phone_columns).issubset(df.columns):
        raise ValueError(f"DataFrame must contain the columns {phone_columns}")

    # Make a copy of the DataFrame to avoid modifying the original
    df = df.copy()

    # Replace "-" with NaN in the phone number columns
    df[phone_columns] = df[phone_columns].replace('-', np.nan)

    # Count the number of NaNs in each phone column
    na_counts = df[phone_columns].isna().sum()

    # Find the column with the lowest number of NaNs
    lowest_na_column = na_counts.idxmin()

    # Find the column with the highest number of NaNs
    highest_na_column = na_counts.idxmax()

    # Create a new "ENRICHED_PHONE_NUMBER" column and fill with entries from the lowest NA column
    df["ENRICHED_PHONE_NUMBER"] = df[lowest_na_column]

    # Fill missing values with valid entries from the highest NA column (if available)
    mask = df["ENRICHED_PHONE_NUMBER"].isna() & ~df[highest_na_column].isna()
    df.loc[mask, "ENRICHED_PHONE_NUMBER"] = df.loc[mask, highest_na_column]

    # Drop rows with missing values in the "ENRICHED_PHONE_NUMBER" column
    df.dropna(subset=["ENRICHED_PHONE_NUMBER"], inplace=True)

    return df


#>>>>>>>>>> - create function sort_and_filter_jobs - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def sort_and_filter_jobs(df, keywords_to_exclude):
    """
    Sorts the data by 'JOB_TITLE' and filters out rows with specific keywords in 'JOB_TITLE'.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the job data.
    keywords_to_exclude (list): List of keywords to exclude from 'JOB_TITLE' (case-insensitive).

    Returns:
    pd.DataFrame: A new DataFrame sorted by 'JOB_TITLE' and filtered based on specified keywords.

    Raises:
    ValueError: If the 'JOB_TITLE' column is not present in the DataFrame.

    Use Case:
    To sort a DataFrame 'df' by 'JOB_TITLE' and exclude job titles containing keywords like 'intern' or 'engineer', use:
    >>> df = pd.read_csv('jobs.csv')
    >>> filtered_df = sort_and_filter_jobs(df, ['intern', 'engineer'])
    """
    if 'JOB_TITLE' not in df.columns:
        raise ValueError("DataFrame must contain a 'JOB_TITLE' column")

    # Sort the data by 'JOB_TITLE'
    sorted_df = df.sort_values(by="JOB_TITLE")

    # Escape keywords for safety in regex
    escaped_keywords = [re.escape(keyword) for keyword in keywords_to_exclude]

    # Filter out rows with 'JOB_TITLE' containing the specified keywords
    pattern = '|'.join(escaped_keywords)
    filtered_df = sorted_df[~sorted_df["JOB_TITLE"].str.lower().str.contains(pattern, na=False)]

    return filtered_df


#>>>>>>>>>> - create function filter_valid_personal_emails - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def filter_valid_personal_emails(df):
    """
    Filters a DataFrame to include only rows with valid email addresses in the 'PERSONAL_EMAIL' column.

    This function checks for the presence of an '@' symbol as a basic criterion for email validation.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the 'PERSONAL_EMAIL' column.

    Returns:
    pd.DataFrame: A new DataFrame with rows containing email addresses that have an '@' symbol.

    Raises:
    ValueError: If the 'PERSONAL_EMAIL' column is not present in the DataFrame.

    Use Case:
    To filter a DataFrame 'df' to include only rows with valid email addresses in 'PERSONAL_EMAIL', use:
    >>> df = pd.read_csv('your_data.csv')
    >>> valid_email_df = filter_valid_personal_emails(df)
    """
    if 'PERSONAL_EMAIL' not in df.columns:
        raise ValueError("DataFrame must contain a 'PERSONAL_EMAIL' column")

    # Basic check for '@' in 'PERSONAL_EMAIL'
    valid_email_df = df[df['PERSONAL_EMAIL'].str.contains('@', na=False)]

    return valid_email_df


#>>>>>>>>>>create - function df_to_excel_openpyxl - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def df_to_excel_openpyxl(dfs, file_path, sheet_names=None):
    """
    Combines multiple pandas DataFrames into a single Excel file with different sheets. 
    Each sheet name includes the name provided in 'sheet_names' and the number of rows in the DataFrame.

    Parameters:
    dfs (list of pd.DataFrame): List of DataFrames to write to Excel.
    file_path (str): Path to save the Excel file.
    sheet_names (list of str, optional): Names for the sheets. If not provided, defaults to 'Sheet_n' format.

    Returns:
    None

    Raises:
    ValueError: If the length of 'sheet_names' does not match the length of 'dfs'.
    Exception: For other issues that may arise during the Excel file creation.

    Use Case:
    To combine multiple DataFrames into a single Excel workbook with each DataFrame in a different sheet, use:
    >>> dfs = [df1, df2, df3]
    >>> df_to_excel_openpyxl(dfs, 'combined.xlsx', ['Data1', 'Data2', 'Data3'])
    """
    if sheet_names and len(dfs) != len(sheet_names):
        raise ValueError("Length of 'sheet_names' must match the number of DataFrames in 'dfs'")

    wb = Workbook()

    # Remove the default sheet created by Workbook
    if wb.active:
        wb.remove(wb.active)

    for i, df in enumerate(dfs):
        if sheet_names:
            sheet_title = f"{sheet_names[i]}_{len(df)}"
        else:
            sheet_title = f"Sheet_{i+1}_{len(df)}"

        # Ensure sheet name is within Excel's limit
        sheet_title = sheet_title[:31]

        ws = wb.create_sheet(sheet_title)
        ws.append(df.columns.tolist())
        for row in df.values:
            ws.append(row.tolist())

    try:
        wb.save(file_path)
    except Exception as e:
        raise Exception(f"An error occurred while saving the file: {e}")



#>>>>>>>>>>create - function list files in a path ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def list_files_in_folder(folder_path):
    """
    Lists all files in the specified folder, excluding subdirectories.

    Parameters:
    folder_path (str): The path to the folder whose files need to be listed.

    Returns:
    list: A list of filenames (str) found in the folder. Returns an empty list if the folder doesn't exist or an error occurs.

    Use Case:
    To get a list of all files in a specific folder, use:
    >>> file_list = list_files_in_folder('/path/to/folder')
    """
    try:
        file_list = os.listdir(folder_path)
        # Filter out subfolders and keep only files
        file_list = [file for file in file_list if os.path.isfile(os.path.join(folder_path, file))]
        return file_list
    except OSError as e:
        print(f"Error occurred while listing files in the folder '{folder_path}': {e}")
        return []


#>>>>>>>>>> - create function filter usa_states - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def filter_usa_states(df):
    """
    Filters a DataFrame to include rows with valid US state abbreviations or valid ZIP codes when the state is '-'.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter. Requires 'PERSONAL_STATE' and 'PERSONAL_ZIP' columns.

    Returns:
    pd.DataFrame: The filtered DataFrame containing only rows with valid US states or ZIP codes.

    Raises:
    ValueError: If the required columns ('PERSONAL_STATE' and 'PERSONAL_ZIP') are not present in the DataFrame.

    Use Case:
    To filter a DataFrame 'df' for rows with valid US states or ZIP codes, use:
    >>> df = pd.read_csv('your_file.csv')
    >>> filtered_df = filter_usa_states(df)
    """
    us_state_abbreviations = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    def is_valid_zip(zip_code):
        pattern = re.compile(r'^\d{5}(-\d{4})?$')
        return pattern.match(zip_code) is not None

    # Check for required columns and apply filtering logic
    if 'PERSONAL_STATE' in df.columns and 'PERSONAL_ZIP' in df.columns:
        state_or_zip_valid = (
            df['PERSONAL_STATE'].isin(us_state_abbreviations) |
            ((df['PERSONAL_STATE'] == '-') & df['PERSONAL_ZIP'].apply(is_valid_zip))
        )
        return df[state_or_zip_valid]
    else:
        raise ValueError("Required columns 'PERSONAL_STATE' and 'PERSONAL_ZIP' not found in DataFrame")



#>>>>>>>>>> - filter_and_label_valid_addresses -  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def filter_and_label_valid_addresses(df):
    """
    Filters a DataFrame to retain rows with valid addresses and adds two new columns:
    'VALID_ADDRESS' containing the first valid address and 'ADDRESS_USED' indicating 
    the field name of the valid address used. A valid address is one that is not NaN, not 
    just a hyphen, and does not contain 'P.O. Box' or variations of it.

    Parameters:
    df (pd.DataFrame): DataFrame with address columns to be processed.

    Returns:
    pd.DataFrame: Modified DataFrame with only valid address rows and added columns.
    int: The count of valid addresses found.

    Raises:
    ValueError: If the input is not a DataFrame or required columns are missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    address_fields = [
        'PERSONAL_ADDRESS', 'PERSONAL_ADDRESS_2',
        'PROFESSIONAL_ADDRESS', 'PROFESSIONAL_ADDRESS_2',
        'COMPANY_ADDRESS', 'COMPANY_ADDRESS_2'
    ]

    # Verify if all required columns are present in the DataFrame
    missing_cols = [col for col in address_fields if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    po_box_pattern = re.compile(r'p\.?\s*o\.?\s*box', re.IGNORECASE)

    def is_valid_address(row):
        for field in address_fields:
            address = row[field]
            if pd.isna(address) or address == "-":
                continue
            if not po_box_pattern.search(address):
                return address, field
        return None, None

    address_info = df.apply(is_valid_address, axis=1).apply(pd.Series)
    df['VALID_ADDRESS'] = address_info[0]
    df['ADDRESS_USED'] = address_info[1]
    valid_addresses_count = df['VALID_ADDRESS'].notna().sum()
    df = df[df['VALID_ADDRESS'].notna()]

    return df


#>>>>>>>>>> - filter for vaild business and personal email-  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def filter_by_valid_business_personal_email(df, validation_column="BUSINESS_EMAIL_VALIDATION_STATUS", business_email_column="BUSINESS_EMAIL", personal_email_column="PERSONAL_EMAIL"):
    """
    Modifies a DataFrame to create a new column 'Valid_Business_Email'. This column contains
    the business email if it's validated as 'Valid' in the specified validation column. Otherwise,
    it uses the personal email, selecting an alternate email from a list of personal emails if the business email is not unique.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        validation_column (str): The name of the column containing email validation status.
        business_email_column (str): The name of the column containing business email addresses.
        personal_email_column (str): The name of the column containing personal email addresses.

    Returns:
        pd.DataFrame: A modified DataFrame with an additional column 'Valid_Business_Email'.

    Use Case:
    Assume a DataFrame 'df' with columns 'BUSINESS_EMAIL', 'PERSONAL_EMAIL', and 'BUSINESS_EMAIL_VALIDATION_STATUS'.
    If 'BUSINESS_EMAIL_VALIDATION_STATUS' is 'Invalid', use 'PERSONAL_EMAIL'. If 'PERSONAL_EMAIL' contains multiple emails separated by semicolons, choose an email different from 'BUSINESS_EMAIL'.
    >>> df = pd.DataFrame({
        'BUSINESS_EMAIL': ['john@example.com', 'jane@example.com'],
        'PERSONAL_EMAIL': ['john.personal@example.com;john.other@example.com', 'jane.personal@example.com'],
        'BUSINESS_EMAIL_VALIDATION_STATUS': ['Invalid', 'Valid']
    })
    >>> modified_df = filter_by_valid_business_personal_email(df)
    This modifies 'df' to include a 'Valid_Business_Email' column with the appropriate email addresses.
    """
    df_processed = df.copy()

    # Determine whether each business email is valid
    is_valid = df_processed[validation_column].str.contains("Valid", case=False, na=False)

    def get_valid_email(business_email, personal_emails, is_valid_email):
        if is_valid_email:
            return business_email
        else:
            personal_emails_list = personal_emails.split(',') if isinstance(personal_emails, str) else [personal_emails]
            # Select an alternate personal email if available, or the first one in the list
            return personal_emails_list[1] if len(personal_emails_list) > 1 else personal_emails_list[0]

    df_processed['Valid_Business_Email'] = df_processed.apply(lambda row: get_valid_email(row[business_email_column], row[personal_email_column], is_valid[row.name]), axis=1)

    return df_processed

#>>>>>>>>>>>>>>>> Enrich email function> - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def enrich_email(df, validation_column="BUSINESS_EMAIL_VALIDATION_STATUS", 
                                            business_email_column="BUSINESS_EMAIL", 
                                            personal_email_column="PERSONAL_EMAIL",
                                            programmatic_email_column="PROGRAMMATIC_BUSINESS_EMAILS"):
    """
    Modifies a DataFrame to create a new column 'Valid_Business_Email'. This column contains
    the business email if it's validated as 'Valid' in the specified validation column. Otherwise,
    it uses the personal email. If neither business nor personal email is available, it selects 
    the first email from the 'PROGRAMMATIC_BUSINESS_EMAILS' column.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        validation_column (str): The name of the column containing email validation status.
        business_email_column (str): The name of the column containing business email addresses.
        personal_email_column (str): The name of the column containing personal email addresses.
        programmatic_email_column (str): The name of the column containing a list of programmatic emails.

    Returns:
        pd.DataFrame: A modified DataFrame with an additional column 'Valid_Business_Email'.
    """

    df_processed = df.copy()

    def get_valid_email(business_email, personal_email, programmatic_email, is_valid_email):
        if is_valid_email and business_email != '-':
            return business_email
        elif personal_email and personal_email != '-':
            return personal_email.split(',')[0]  # Assumes personal_email is comma-separated
        elif programmatic_email and programmatic_email != '-':
            return programmatic_email.split(',')[0]  # Assumes programmatic_email is comma-separated
        else:
            return None

    # Apply the logic row-wise
    df_processed['Valid_Business_Email'] = df_processed.apply(
        lambda row: get_valid_email(row[business_email_column], 
                                    row[personal_email_column], 
                                    row[programmatic_email_column], 
                                    row[validation_column].lower() == "valid"),
        axis=1)

    return df_processed


#>>>>>>>>>> - create csv file -  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def save_df_to_csv(df, file_name):
    """
    Saves a pandas DataFrame to a CSV file, creating the directory if it does not exist.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        file_name (str): The file name for the CSV file.

    Returns:
        None

    Use Case:
    To save a DataFrame 'df' to a CSV file named 'data.csv' in the 'Output_list_DataBase' directory, use:
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> save_df_to_csv(df, 'data')
    This will save 'df' as a CSV file named 'data.csv' in the 'Output_list_DataBase' directory.
    """
    directory = "Output_list_DataBase"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, f"{file_name}.csv")

    try:
        df.to_csv(file_path, index=False)
        print(f"DataFrame successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving DataFrame to CSV: {e}")

#>>>>>>>>>> - filter by target industry -  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#taget industry
def filter_by_target_industries(df, target_industries):
    """
    Filters a DataFrame to include only rows that belong to the specified target industries.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    target_industries (list): List of target industries.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    filtered_df = df[df['PRIMARY_INDUSTRY'].isin(target_industries)]

    return filtered_df


#>>>>>>>>>> - drop_rows_with_hyphen -  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def drop_rows_with_hyphen(df, columns):
    """
    Drops rows in a DataFrame where specified columns contain a hyphen ("-").

    Args:
        df (pd.DataFrame): The DataFrame to process.
        columns (list): List of column names to check for hyphens.

    Returns:
        pd.DataFrame: A new DataFrame with rows containing hyphens in specified columns dropped.
    """
    # Ensure columns is a list, even if a single column name is provided
    if not isinstance(columns, list):
        columns = [columns]

    # Drop rows where any of the specified columns contain a hyphen
    for column in columns:
        if column in df.columns:
            df = df[df[column] != '-']
    
    return df
#>>>>>>>>>> - merge csv files -  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def merge_csv_files(folder_path, output_file, columns_to_check=None):
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


#>>>>>>>>>> - Slit columns by separator function -  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def split_columns_by_separator(df, columns, separator=",", keep_non_missing_only=True, drop_duplicates=True):
    """
    Splits the values in specified columns of a DataFrame separated by a given separator into distinct columns,
    first converting the column to a string type. Optionally keeps only those split columns that do not have any missing values and drops duplicated columns.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        columns (list of str or str): The names of the columns to split. Can be a single column name or a list of names.
        separator (str): The separator used to split the column values.
        keep_non_missing_only (bool): If True, only keeps split columns without missing values.
        drop_duplicates (bool): If True, drops duplicated columns after the split.

    Returns:
        pd.DataFrame: A DataFrame with the original columns and the new split columns, optionally filtered for non-missing values and without duplicates.

    Use Case Example:
        # Create a sample DataFrame
        data = {'Name': ['Alice', 'Bob', 'Charlie'],
                'Interests': ['Reading,Writing', 'Painting', 'Hiking,Cycling,Swimming']}
        sample_df = pd.DataFrame(data)

        # Split the 'Interests' column
        updated_df = split_columns_by_separator(sample_df, 'Interests', separator=',')

        The resulting 'updated_df' will have the original 'Name' and 'Interests' columns,
        as well as additional columns 'Interests_1', 'Interests_2', etc., each containing a split value from the 'Interests' column.
    """
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")

        # Convert the column to string type and then split
        split_columns = df[column].astype(str).str.split(separator, expand=True)

        # Create new column names based on the number of splits
        new_columns = [f"{column}_{i+1}" for i in range(split_columns.shape[1])]
        split_columns.columns = new_columns

        # Optionally filter out columns with missing values
        if keep_non_missing_only:
            split_columns = split_columns.dropna(axis=1)

        # Optionally drop duplicated columns
        if drop_duplicates:
            split_columns = split_columns.T.drop_duplicates().T

        # Concatenate with the original DataFrame
        df = pd.concat([df, split_columns], axis=1)

    return df

# >>>>>>>>>>>>>>>> - LiveRamp formatter function - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def liveramp_formatter(df):
    """
    Formats a given DataFrame using a specific column mapping, adds an autogenerated unique 4-digit 'Client Customer ID' to each row, 
    and checks if 'PhoneNumber1' and 'PhoneNumber2' are the same. If they are, 'PhoneNumber2' is filled with NaN.
    
    This function is useful for preparing data for processes that require standardized column names and unique identifiers.
    
    Args:
        df (pd.DataFrame): The DataFrame to format.

    Returns:
        pd.DataFrame: A formatted DataFrame with columns renamed and selected as per the mapping, an added 'Client Customer ID' column,
                      and 'PhoneNumber2' set to NaN if it's the same as 'PhoneNumber1'.

    Raises:
        KeyError: If any of the specified columns in the mapping do not exist in the original DataFrame.

    Use Case Example:
        # Suppose we have a DataFrame 'data_df' with columns like 'FIRST_NAME', 'LAST_NAME', 'VALID_ADDRESS', etc.
        # and 'ENRICHED_PHONE_NUMBER', 'MOBILE_PHONE' for phone numbers.
        # We can use this function to format 'data_df' for further processing.

        # Example DataFrame
        data = {
            'FIRST_NAME': ['Alice', 'Bob'],
            'LAST_NAME': ['Smith', 'Johnson'],
            'ENRICHED_PHONE_NUMBER': ['1234567890', '0987654321'],
            'MOBILE_PHONE': ['1234567890', '1234567890'],
            # ... other columns ...
        }
        sample_df = pd.DataFrame(data)

        # Format the DataFrame
        formatted_df = liveramp_formatter(sample_df)

        # The 'formatted_df' will now have a 'Client Customer ID', renamed columns as per the mapping,
        # and 'PhoneNumber2' will be NaN where it's the same as 'PhoneNumber1'.
    """
    column_mapping = {
        'First Name': 'FIRST_NAME',
        'Last Name': 'LAST_NAME',
        'Street Address 1': 'VALID_ADDRESS',
        'Street Address 2': 'PROFESSIONAL_ADDRESS',
        'City': 'PERSONAL_CITY',
        'State': 'PERSONAL_STATE',
        'Zip Code': 'PERSONAL_ZIP',
        'Zip Code Plus 4': 'PERSONAL_ZIP4',
        'Email1': 'Valid_Business_Email',
        'Email2': 'PROGRAMMATIC_BUSINESS_EMAILS_1',
        'Email3': 'PROGRAMMATIC_BUSINESS_EMAILS_2', 
        'PhoneNumber1': 'ENRICHED_PHONE_NUMBER',
        'PhoneNumber2': 'MOBILE_PHONE'
    }

    # Check if all specified columns in the mapping exist in the original DataFrame
    for original_col in column_mapping.values():
        if original_col not in df.columns:
            raise KeyError(f"Column '{original_col}' not found in DataFrame")

    # Generate a unique 4-digit ID for each row
    df['Client Customer ID'] = [random.randint(1000, 9999) for _ in range(len(df))]

    # Select and rename columns based on the mapping
    formatted_df = df[['Client Customer ID'] + list(column_mapping.values())].rename(columns={v: k for k, v in column_mapping.items()})

    # Check if PhoneNumber1 and PhoneNumber2 are the same, if so, set PhoneNumber2 to NaN
    formatted_df['PhoneNumber2'] = np.where(formatted_df['PhoneNumber1'] == formatted_df['PhoneNumber2'], np.nan, formatted_df['PhoneNumber2'])
    
    # Check if 'Street Address 1 and Street Address 2 are the same, if so, set PhoneNumber2 to NaN
    formatted_df['Street Address 2'] = np.where(formatted_df['Street Address 1'] == formatted_df['Street Address 2'], np.nan, formatted_df['Street Address 2'])
    


    return formatted_df

#>>>>>>>>>>>>> liveramp adlist creator function >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def liveramp_adlist_creator(file_path: str, target_industries: list, adlist_name: str, **kwargs):
    """
    Processes an input data file to generate a formatted advertising list following specific criteria. 
    The data is filtered by target industries and USA states, validated for addresses and phone numbers, 
    and formatted in the Liveramp specified format.

    Args:
        file_path (str): Path to the input data file.
        target_industries (list): List of target industries for filtering.
        adlist_name (str): Name for the output advertising list file.
        **kwargs: Additional arguments to pass to filtering and formatting functions.

    Returns:
        str: A message indicating the status of the file saving process.

    Raises:
        Exception: If any errors occur during the data processing steps.
    
    Use Case:
    >>> primary_industries=['Advertising Services', 'Marketing','Book And Periodical Publishing', 'Entertainment Providers', 'Events Services','Broadcast Media Production And Distribution','Public Relations And Communications Services', 'Online Audio And Video Media', 'Printing Services','Newspaper Publishing', 'Newspapers']
    >>> liveramp_adlist_creator(file_path="out_put file path", target_industries=primary_industries, output_file_name='name of list created')
    """

    try:
        # Load data from the file
        df = get_data(file_path)
        
        # Filter by target industries
        df_industries = filter_by_target_industries(df, target_industries)

        # Filter for USA states only
        state_df = filter_usa_states(df_industries)
    
        # Filter for valid addresses
        valid_address_df = filter_and_label_valid_addresses(state_df.copy())
    
        # Get valid phone numbers
        valid_numbers = enrich_phone_numbers(valid_address_df.copy())
   
        # Filter for valid business and personal emails
        valid_number_email_df = filter_by_valid_business_personal_email(
            valid_numbers,
            validation_column="BUSINESS_EMAIL_VALIDATION_STATUS",
            business_email_column="BUSINESS_EMAIL",
            personal_email_column="PERSONAL_EMAIL"
        )
    
        # Split programmatic business emails into separate columns
        df_program_emails = split_columns_by_separator(
            valid_number_email_df, 
            'PROGRAMMATIC_BUSINESS_EMAILS', 
            separator=',', 
            keep_non_missing_only=True, 
            drop_duplicates=True
        )
    
        # Format data in Liveramp format
        formatted_df = liveramp_formatter(df_program_emails)
    
        # Save to file
        output_message = save_df_to_csv(formatted_df, adlist_name)

        return output_message

    except Exception as e:
        # Handle any exceptions that occur during the process
        return f"An error occurred: {str(e)}"
    
#>>>>>>>>> email list creator function- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def email_list_creator(file_path: str, target_industries: list, email_list_name: str):
    """
    Creates an email list from a data file. The process includes loading data, filtering by target industries and USA states, 
    enriching phone numbers, removing rows with missing email values, selecting specific columns, renaming them, 
    and saving the processed data to a CSV file.

    Args:
        file_path (str): The path to the data file.
        target_industries (list): List of industries to filter the data.
        email_list_name (str): The name for the output CSV file.

    Returns:
        str: A message indicating the success or failure of the process.

    Raises:
        KeyError: If a required column is missing in the DataFrame.
        Exception: For other errors that may occur.
    
    Use case:
    >>> target_industries=["sales","media", "Printing"]
    >>> file_path = "./data/df.csv"
    >>> email_list_name = "email_list"
    >>> email_list_creator(file_path, target_industries, email_list_name)
    """
    try:
        # Load data from the file
        df = get_data(file_path)
        
        # Filter by target industries
        df_industries = filter_by_target_industries(df, target_industries)

        # Filter for USA states only
        state_df = filter_usa_states(df_industries)
        
        # Enrich email with all email fields
        valid_email = enrich_email(state_df.copy())
          
        # Get valid phone numbers
        #valid_numbers = enrich_phone_numbers(valid_email.copy()) #====== not sure its included
   
        # Drop rows with missing email
        clean_df = drop_rows_with_hyphen(valid_email, ["Valid_Business_Email"])
        
        # Select and rename specific columns
        column_mapping = {
            'First Name': 'FIRST_NAME',
            'Last Name': 'LAST_NAME',
            'Email': 'Valid_Business_Email',
            #'Phone Number': 'ENRICHED_PHONE_NUMBER', #====== note sure if its included
        }

        # Check if all specified columns in the mapping exist in the original DataFrame
        for original_col in column_mapping.values():
            if original_col not in clean_df.columns:
                raise KeyError(f"Column '{original_col}' not found in DataFrame")
        
        # Select and rename columns
        final_df = clean_df[list(column_mapping.values())].rename(columns={v: k for k, v in column_mapping.items()})

        # Save to file
        output_message = save_df_to_csv(final_df, email_list_name)

        return output_message

    except Exception as e:
        # Handle any exceptions that occur during the process
        return f"An error occurred: {str(e)}"

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>> - ed-  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>