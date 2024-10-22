import streamlit as st
import pandas as pd
from src.tracklist_processor import process_and_store_tracklist
from src.data_management import read_and_display_sorted_data, get_summary_stats

st.title("Tracklist Organizer")

st.write("Paste your tracklist below:")

example_tracklist = """
1. mall grab - ive always liked grime (0:00)
2. dj seinfeld - ruff hysteria (2:00)
3. edmondson - diamond life (4:00)
4. dj boring - winona (6:00)
"""

input_tracklist = st.text_area("Tracklist", height=200, value=example_tracklist)
batch_name = st.text_input("Enter a batch name (optional):", "")

if st.button("Process Tracklist"):
    if input_tracklist:
        result_df = process_and_store_tracklist(input_tracklist, batch_name)
        st.write("Processed tracklist:")
        st.dataframe(result_df)
        
        st.write("Top 5 most recent entries (Log Table):")
        recent_entries_log = read_and_display_sorted_data("artifacts/tracklist_log")
        st.dataframe(recent_entries_log)
        
        st.write("Top 5 most recent entries (De-duplicated View Table):")
        recent_entries_view = read_and_display_sorted_data("artifacts/tracklist_view")
        st.dataframe(recent_entries_view)
    else:
        st.warning("Please enter a tracklist before processing.")


# Add a section to display all entries in the view table
if st.button("Show All De-duplicated Entries"):
    all_entries_view = read_and_display_sorted_data("artifacts/tracklist_view", num_rows=None)
    st.write("All De-duplicated Entries:")
    st.dataframe(all_entries_view)


# Add a button to display summary statistics
if st.button("Show Summary Statistics"):
    st.header("Summary Statistics")
    stats = get_summary_stats()

    if stats['log']['total_tracks'] > 0 or stats['view']['distinct_songs'] > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Log Table Statistics")
            total_log = stats['log']['total_tracks']
            st.write(f"Total tracks submitted: {total_log}")
            st.write(f"Number of distinct runs: {stats['log']['distinct_runs']}")
            st.write(f"Tracks with unknown title: {stats['log']['unknown_title_count']} ({stats['log']['unknown_title_count']/total_log:.1%})")
            st.write(f"Tracks with unknown artist: {stats['log']['unknown_artist_count']} ({stats['log']['unknown_artist_count']/total_log:.1%})")
            st.write(f"Tracks with unknown title or artist: {stats['log']['unknown_track_count']} ({stats['log']['unknown_track_count']/total_log:.1%})")

        with col2:
            st.subheader("View Table Statistics")
            total_view = stats['view']['distinct_songs']
            st.write(f"Number of distinct songs: {total_view}")
            st.write(f"Number of distinct artists: {stats['view']['distinct_artists']}")
            st.write(f"Number of runs that added new songs: {stats['view']['runs_with_new_songs']}")
            st.write(f"Tracks with unknown title: {stats['view']['unknown_title_count']} ({stats['view']['unknown_title_count']/total_view:.1%})")
            st.write(f"Tracks with unknown artist: {stats['view']['unknown_artist_count']} ({stats['view']['unknown_artist_count']/total_view:.1%})")
            st.write(f"Tracks with unknown title or artist: {stats['view']['unknown_track_count']} ({stats['view']['unknown_track_count']/total_view:.1%})")
    else:
        st.info("No data available yet. Process a tracklist to see summary statistics.")
