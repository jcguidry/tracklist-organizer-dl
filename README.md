# AI-Powered Music Playlist Organizer and Downloader

This project creates a comprehensive tool for organizing, managing, and downloading music playlists using AI and data lake technologies. It focuses on cleaning up and structuring tracklists from YouTube videos and comments, as well as providing download functionality for personal use.

## Project Background

- YouTube hosts a wealth of music playlists and mixes.
- Creators or commenters often include tracklists in video descriptions or comments.
- These tracklists are frequently poorly formatted and include timestamps, making them difficult to use.
- This tool structures these song lists and provides the ability to download them for personal use.

## Key Features

1. AI-powered cleanup of unstructured tracklists
2. Structured storage of tracklist data using Delta Lake
3. Fast de-duplication and data management using DuckDB
4. Optional batch naming for groups of songs
5. Lookup of tracks on YouTube and URL storage
6. Integration with SpotDL for music downloading (for personal use only)
7. Track management and download status tracking

## Workflow

1. User inputs an unstructured list of songs (pasted from a mix tracklist)
2. User optionally enters a "batch name" for the group of songs
3. AI performs text cleanup and structuring
4. Data is loaded into a local structured data lake using pandas, deltalake, and pyarrow
5. DuckDB is used for fast de-duplication, querying, and management of songs
6. Lookup of tracks on YouTube and storage of URLs
7. Download and storage of tracks using SpotDL library

## Data Management Approach

1. **Log Table**: A Delta Lake table that acts as an append-only log for all incoming tracklist data
2. **View Table**: A separate Delta Lake table that presents a de-duplicated view of the log table
   - Updated with each run
   - Uses DuckDB for fast processing, capable of handling billions of records
   - Implements QUALIFY to show each unique track once, with its first_added_ts timestamp

## Track Management Features

- Identify which tracks were found on YouTube
- Track download attempts to avoid redundant operations
- Delivery of tracks to folders aliased with the "batch name"

## Download Functionality

- Utilizes SpotDL library for high-quality music downloads
- Cross-references songs from Spotify and finds them on YouTube
- Can accept YouTube URLs directly
- Supports YouTube Music Premium token for highest quality downloads

## Note on Music Downloads

The music download functionality is intended for personal use only. Any music downloaded through this tool should not be used for commercial purposes and must comply with copyright laws and regulations.

## Getting Started

(Add instructions for setting up and running the project)

## Contributing

(Add guidelines for contributing to the project)

## License

(Add appropriate license information)
