import os
from datetime import datetime, timezone
import pandas as pd
from deltalake import write_deltalake, DeltaTable
import pyarrow as pa
import duckdb
import pytz

# Configure pandas to display all rows
pd.set_option('display.max_rows', None)

def create_tracklist_dataframe(processed_tracklist, batch_name):
    """
    Convert processed tracklist to DataFrame and add metadata.
    
    Args:
        processed_tracklist (dict): Dictionary containing track information.
        batch_name (str): Optional name for the batch of tracks.
    
    Returns:
        pd.DataFrame: DataFrame with track information and metadata.
    """
    df = pd.DataFrame(processed_tracklist['tracks'])
    df['artist_title'] = df['artist'] + ' - ' + df['title']
    df['load_ts'] = datetime.now(timezone.utc)
    df['batch_name'] = batch_name
    return df

def deduplicate_delta_table(table_path):
    """
    Remove duplicate entries from the Delta table based on artist and title.
    
    Args:
        table_path (str): Path to the Delta table.
    
    Returns:
        None
    """
    # Read the entire table
    dt = DeltaTable(table_path)
    df = dt.to_pandas()
    
    # Drop duplicates based on artist and title, keeping the latest entry
    df_deduped = df.sort_values('load_ts', ascending=False).drop_duplicates(subset=['artist', 'title'], keep='first')
    
    # Overwrite the table with de-duplicated data
    write_deltalake(table_path, df_deduped, mode="overwrite")
    
    print(f"De-duplication complete. Removed {len(df) - len(df_deduped)} duplicate entries.")

def create_view_table(log_table_path, view_table_path):
    """
    Create a de-duplicated view table using DuckDB for fast processing.
    
    Args:
        log_table_path (str): Path to the log Delta table.
        view_table_path (str): Path to save the view Delta table.
    """
    # Check if the log table exists and has data
    try:
        dt = DeltaTable(log_table_path)
        if dt.files() == []:
            print("Log table is empty. Skipping view table creation.")
            return
    except Exception as e:
        print(f"Error reading log table: {e}")
        return

    # Connect to DuckDB
    con = duckdb.connect(':memory:')
    
    # Read the log table into DuckDB
    con.execute(f"CREATE TABLE log_table AS SELECT * FROM delta_scan('{log_table_path}')")
    
    # Get the local timezone
    local_tz = pytz.timezone('America/New_York')  # Replace with your local timezone
    
    # Create the de-duplicated view with formatted load_ts
    query = """
    SELECT 
        artist,
        title,
        artist_title,
        batch_name,
        strftime(load_ts AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York', '%Y-%m-%d %I:%M:%S %p') as formatted_load_ts
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY artist, title ORDER BY load_ts) as rn
        FROM log_table
    ) subquery
    WHERE rn = 1
    ORDER BY load_ts DESC
    """
    
    result = con.execute(query).fetchdf()
    
    # Write the result to a new Delta table
    write_deltalake(view_table_path, result, mode="overwrite")
    
    print(f"View table created at {view_table_path}")

def read_and_display_sorted_data(table_path, num_rows=5):
    """
    Read and display sorted data from a Delta table.
    
    Args:
        table_path (str): Path to the Delta table.
        num_rows (int): Number of rows to display.
    
    Returns:
        pd.DataFrame: Sorted DataFrame with the specified number of rows.
    """
    try:
        dt = DeltaTable(table_path)
        df = dt.to_pandas()
        sorted_df = df.sort_values('formatted_load_ts' if 'formatted_load_ts' in df.columns else 'load_ts', ascending=False)
        if num_rows is not None:
            sorted_df = sorted_df.head(num_rows)
        return sorted_df
    except Exception as e:
        print(f"Error reading table {table_path}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

def get_summary_stats():
    """
    Calculate summary statistics for the log and view tables using DuckDB and PyArrow.
    
    Returns:
        dict: A dictionary containing summary statistics for both tables.
    """
    con = duckdb.connect(':memory:')
    
    log_table_path = "artifacts/tracklist_log"
    view_table_path = "artifacts/tracklist_view"
    
    # Read Delta tables and convert to PyArrow tables
    try:
        log_delta = DeltaTable(log_table_path)
        log_table = log_delta.to_pyarrow_table()
        
        view_delta = DeltaTable(view_table_path)
        view_table = view_delta.to_pyarrow_table()
    except Exception as e:
        print(f"Error reading Delta tables: {e}")
        return {
            'log': {'total_tracks': 0, 'distinct_runs': 0},
            'view': {'distinct_songs': 0, 'distinct_artists': 0, 'runs_with_new_songs': 0}
        }
    
    # Register tables in DuckDB
    con.register('log_table', log_table)
    con.register('view_table', view_table)
    
    # Update log stats query
    log_stats = con.execute("""
        SELECT 
            COUNT(*) as total_tracks,
            COUNT(DISTINCT load_ts) as distinct_runs,
            COUNT(DISTINCT batch_name) as distinct_batches,
            COUNT(*) FILTER (WHERE title = 'Unknown Title') as unknown_title_count,
            COUNT(*) FILTER (WHERE artist = 'Unknown Artist') as unknown_artist_count,
            COUNT(*) FILTER (WHERE title = 'Unknown Title' OR artist = 'Unknown Artist') as unknown_track_count
        FROM log_table
    """).fetchone()
    
    # Update view stats query
    view_stats = con.execute("""
        SELECT 
            COUNT(*) as distinct_songs,
            COUNT(DISTINCT artist) as distinct_artists,
            COUNT(DISTINCT formatted_load_ts) as runs_with_new_songs,
            COUNT(DISTINCT batch_name) as distinct_batches,
            COUNT(*) FILTER (WHERE title = 'Unknown Title') as unknown_title_count,
            COUNT(*) FILTER (WHERE artist = 'Unknown Artist') as unknown_artist_count,
            COUNT(*) FILTER (WHERE title = 'Unknown Title' OR artist = 'Unknown Artist') as unknown_track_count
        FROM view_table
    """).fetchone()
    
    return {
        'log': {
            'total_tracks': log_stats[0],
            'distinct_runs': log_stats[1],
            'distinct_batches': log_stats[2],
            'unknown_title_count': log_stats[3],
            'unknown_artist_count': log_stats[4],
            'unknown_track_count': log_stats[5]
        },
        'view': {
            'distinct_songs': view_stats[0],
            'distinct_artists': view_stats[1],
            'runs_with_new_songs': view_stats[2],
            'distinct_batches': view_stats[3],
            'unknown_title_count': view_stats[4],
            'unknown_artist_count': view_stats[5],
            'unknown_track_count': view_stats[6]
        }
    }
