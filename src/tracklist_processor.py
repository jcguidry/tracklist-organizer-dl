from src.data_management import create_tracklist_dataframe, create_view_table
from src.ai_funcs import get_tracklist
from deltalake import write_deltalake, DeltaTable

def process_and_store_tracklist(input_tracklist, batch_name):
    """
    Process the input tracklist, convert it to a DataFrame, and store it.
    
    Args:
        input_tracklist (str): Raw tracklist input.
        batch_name (str): Optional name for the batch of tracks.
    
    Returns:
        pd.DataFrame: Processed tracklist as a DataFrame.
    """
    # Process the input tracklist
    processed_tracklist = get_tracklist(input_tracklist)
    
    # Create and display the DataFrame
    df = create_tracklist_dataframe(processed_tracklist, batch_name)
    
    # Check if the table already exists
    log_table_path = "artifacts/tracklist_log"
    view_table_path = "artifacts/tracklist_view"
    
    try:
        # Try to append to the existing table
        write_deltalake(log_table_path, df, mode="append", schema_mode='merge')
    except Exception as e:
        print(f"Error appending to existing table: {e}")
        # If the table doesn't exist or there's another error, create a new one
        write_deltalake(log_table_path, df)
    
    # Create or update the view table
    create_view_table(log_table_path, view_table_path)
    
    return df
