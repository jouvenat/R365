#import pandas as pd
from datetime import date
from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
import os
import subprocess

def process_conversion(input_file_path: str, reference_file_path: str, selected_date: str):
    # Clear previous output
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Starting conversion process...\n")
    try:
        #read the input csv file
        output_text.insert(tk.END, f"Reading input file: {input_file_path}\n")
        input_df = pd.read_csv(input_file_path)
    except Exception as e:
        output_text.insert(tk.END, f"Error reading input file: {e}\n", "error")
        return
    
    #read the reference csv file
    output_text.insert(tk.END, f"Reading reference file: {reference_file_path}\n")
    try:
        reference_df = pd.read_csv(reference_file_path)
    except Exception as e:
        output_text.insert(tk.END, f"Error reading reference file: {e}\n", "error")
        return
        
    
    #create an empty output dataframe with the column names
    output_df = pd.DataFrame(columns=['Ordering Location', 'Order Guide', 'Date', 'Commissary Item', 'Quantity'])
    #create an empty dataframe for the errors
    error_df = pd.DataFrame(columns=['Product Name'])
    nb_errors = 0
    
    #for each row in the input csv file, find the corresponding row in the conversion csv file
    total_rows = len(input_df)
    output_text.insert(tk.END, f"Processing {total_rows} items...\n")
    
    for index, row in input_df.iterrows():
        #find the corresponding row in the conversion csv file
        match = reference_df.loc[reference_df['BlueCart Name'] == row['Product Name']]
       
        #if there is a match, add the row to the output dataframe       
        if not match.empty:
            conversion_row = match.iloc[0]
            new_row = {'Ordering Location': conversion_row['Location'], 'Order Guide': conversion_row['Order Guides'], 'Date': selected_date, 'Commissary Item': conversion_row['R365 Commissary Item'], 'Quantity': row['Total']}
            output_df = pd.concat([output_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            new_row = {'Product Name': row['Product Name']}
            error_df = pd.concat([error_df, pd.DataFrame([new_row])], ignore_index=True)
            nb_errors += 1
            output_text.insert(tk.END, f"Warning: No match found for '{row['Product Name']}'\n")
        
        # Update progress
        if (index + 1) % 10 == 0:  # Update every 10 items
            output_text.insert(tk.END, f"Processed {index + 1}/{total_rows} items...\n")
            output_text.see(tk.END)  # Auto-scroll to bottom
            root.update()  # Update the GUI

    #create a filename with the current date and time
    filename = 'output/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_output.csv'
    #write the output dataframe to a csv file
    output_df.to_csv(filename, index=False)
    
    #if there are errors, write the error dataframe to a csv file
    if nb_errors > 0:
        error_filename = 'output/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_error.csv'
        error_df.to_csv(error_filename, index=False)
        output_text.insert(tk.END, f"\nConversion complete but with {nb_errors} missing items.\n", "error")
        output_text.insert(tk.END, f"The file {error_filename} contains the details.\n", "error")
        output_text.insert(tk.END, f"You likely need to add the missing items to the reference file and run the conversion again.\n", "error")
    else:
        output_text.insert(tk.END, "\nConversion completed successfully!\n")
        output_text.insert(tk.END, f"\nThe file to import in R365 is: {filename}\n")
    
    output_text.see(tk.END)  # Auto-scroll to bottom
    root.update()  # Update the GUI

def choose_file(title: str, file_path: tk.StringVar):
    filename = filedialog.askopenfilename(
        title="Select " + title,
        filetypes=[("CSV files", "*.csv")]
    )
    if filename:
        file_path.set(filename)

def open_reference_file():
    file_path = 'data/conversion.csv'
    if os.path.exists(file_path):
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        else:  # macOS and Linux
            subprocess.run(['open' if os.name == 'posix' else 'xdg-open', file_path])

# Create the main window
root = tk.Tk()
root.title("Blue Cart Item count to R365 Commissary Order")
root.geometry("600x600")

# Create and pack a frame
frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

#Add a label to explain the process
ttk.Label(frame, text="This utility converts a Blue Cart Item Count CSV file to a R365 Commissary Order CSV file. The converted file can then be imported into R365.",wraplength=500).pack(pady=10)
ttk.Label(frame, text="For this to work properly it uses a reference CSV file that contains all BlueCart items and the corresponding name in R365. If an item is missing in that file, you shall add it and try the conversion again.",wraplength=500).pack(pady=10)

#create a frame for the reference file  
reference_frame = ttk.Frame(frame)
reference_frame.pack(pady=5)
#add a label, a link the file name and a button to open the file with its default program   
reference_file_path = tk.StringVar()
reference_file_name = "data/conversion.csv"
reference_file_path.set(reference_file_name)
ttk.Label(reference_frame, text="Reference file:").pack(side=tk.LEFT, padx=(0,5))
ttk.Button(reference_frame, textvariable=reference_file_path, command=lambda: choose_file("reference file", reference_file_path), style='Link.TButton').pack(side=tk.LEFT, padx=(0,5))
ttk.Button(reference_frame, text="Edit File", command=open_reference_file).pack(side=tk.LEFT)

# Create a style for the link button
style = ttk.Style()
style.configure('Link.TButton', foreground='blue', underline=True)

#add a text field to display the file path
input_file_path = tk.StringVar()
#look inside the current directory for the most recent .csv file
input_file_path.set(os.path.join(os.getcwd(), '*.csv'))
# create a new frame for the file selection
file_selection_frame = ttk.Frame(frame)
file_selection_frame.pack(pady=10, anchor=tk.W)
ttk.Label(file_selection_frame, text="Blue Cart file:").pack(side=tk.LEFT, padx=(0,5))
file_path_entry = ttk.Entry(file_selection_frame, textvariable=input_file_path, width=40)
file_path_entry.pack(side=tk.LEFT, padx=(0,5))

choose_file_button = ttk.Button(file_selection_frame, text="Choose File", command=lambda: choose_file("BlueCart export file",input_file_path))
choose_file_button.pack(side=tk.LEFT)

# Create a frame for date selection elements
date_selection_frame = ttk.Frame(frame)
date_selection_frame.pack(pady=10, anchor=tk.W)

# Add a label
ttk.Label(date_selection_frame, text="Order Date:").pack(side=tk.LEFT, padx=(0,10))

# Add the calendar widget with proper configuration
cal = DateEntry(date_selection_frame, 
                width=12, 
                background='darkblue',
                foreground='white', 
                borderwidth=2,
                date_pattern='yyyy-mm-dd',
                firstweekday='monday',
                showweeknumbers=False)
cal.pack(side=tk.LEFT)

def set_today():
    cal.set_date(datetime.now().date())

def set_tomorrow():
    cal.set_date((datetime.now() + timedelta(days=1)).date())

#add a button to set the date to today
ttk.Button(date_selection_frame, text="Today", command=set_today).pack(side=tk.LEFT, padx=(10,0))
#add a button to set the date to tomorrow
ttk.Button(date_selection_frame, text="Tomorrow", command=set_tomorrow).pack(side=tk.LEFT, padx=(10,0))

#add a frame for the conversion process
conversion_frame = ttk.Frame(frame)
conversion_frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Create a scrollable text area
text_frame = ttk.Frame(conversion_frame)
text_frame.pack(fill=tk.BOTH, expand=True)

# Create the text widget and scrollbar
output_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=output_text.yview)
output_text.configure(yscrollcommand=scrollbar.set)

# Configure text tags
output_text.tag_configure("error", foreground="red")

# Pack the text widget and scrollbar
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Add the convert button
ttk.Button(conversion_frame, text="Convert", 
           command=lambda: process_conversion(input_file_path.get(),reference_file_path.get(),cal.get_date().strftime('%Y-%m-%d'))).pack(pady=10)

# Start the GUI event loop
root.mainloop()
