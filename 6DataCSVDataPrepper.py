# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:54:29 2024

@author: alexb
"""

import os
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Hide the main tkinter window
root = Tk()
root.withdraw()

# Ask the user to select a directory
directory = askdirectory(title="Select the directory containing CSV files")

# Define the column names for the output file
columns = [f"Router{i}BufferWrites" for i in range(16)] + ["Applications (Label Classes)"]

# Set the output file path in the selected directory
output_file_path = os.path.join(directory, "Data-traffic-distribution.csv")

# Initialize the header_written flag to control the header row
header_written = False

# Iterate through each CSV file in the selected directory
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        
        # Read the CSV file, skipping problematic rows
        df = pd.read_csv(file_path, header=None, on_bad_lines='skip')  # Use skip to handle extra columns
        
        # Extract cell A61 (row 60, column 0) from the original CSV
        cell_a61 = df.iat[60, 0] if len(df) > 60 else None  # Safely get A61 if it exists
        cell_a62 = df.iat[61, 0] if len(df) > 60 else None  # Safely get A61 if it exists
        
        # Select rows 33-48 and only the second column (buffer writes)
        selected_rows = df.iloc[32:48, 1:2] 
        transposed_rows = selected_rows.fillna(0).T #Fills empty columns with zero
        
        # Add the value of cell A61 to each row in the selected rows
        if '.' in cell_a61:
            transposed_rows["Applications (Label Classes)"] = cell_a62
        else:
            transposed_rows["Applications (Label Classes)"] = cell_a61
        
        # Set the correct column names for the selected rows
        transposed_rows.columns = columns
        
        # Append the selected rows to the output CSV file
        # Write header only if it's the first file being processed
        transposed_rows.to_csv(output_file_path, mode='a', index=False, header=not header_written)
        
        # Set header_written to True after the first write
        header_written = True
