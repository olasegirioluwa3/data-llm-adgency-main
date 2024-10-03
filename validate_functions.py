import pandas as pd

# validation
def validate_filter_by_target_industries_output(df, target_industries):
    """
    Validates the output of the filter_by_target_industries function.

    Parameters:
    df (pd.DataFrame): The DataFrame to validate.
    target_industries (list): List of target industries used for filtering.

    Returns:
    bool: True if validation is successful, False otherwise.
    """
    if not isinstance(df, pd.DataFrame):
        print("Output is not a DataFrame.")
        return False

    if not df['PRIMARY_INDUSTRY'].isin(target_industries).all():
        print("Some rows do not belong to the target industries.")
        return False

    return True