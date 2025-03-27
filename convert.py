#import pandas as pd
from datetime import date
from datetime import datetime
import pandas as pd
#read the input csv file
input_df = pd.read_csv('data/input.csv')
#read the conversion csv file
conversion_df = pd.read_csv('data/conversion.csv')
#create an empty output dataframe with the column names
output_df = pd.DataFrame(columns=['Ordering Location', 'Order Guide', 'Date', 'Commissary Item', 'Quantity'])
#create an empty dataframe for the errors
error_df = pd.DataFrame(columns=['Product Name'])
#today's date in the format YYYY-MM-DD
today = date.today().strftime('%Y-%m-%d')

#for each row in the input csv file, find the corresponding row in the conversion csv file
for index, row in input_df.iterrows():
    #find the corresponding row in the conversion csv file
    match = conversion_df.loc[conversion_df['BlueCart Name'] == row['Product Name']]
   
    #if there is a match, add the row to the output dataframe       
    if not match.empty:
        conversion_row = match.iloc[0]
        new_row = {'Ordering Location': 'Blue Cart Location', 'Order Guide': conversion_row['Order Guides'], 'Date': today, 'Commissary Item': conversion_row['R365 Commissary Item'], 'Quantity': row['Total']}
        output_df = pd.concat([output_df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        new_row = {'Product Name': row['Product Name']}
        error_df = pd.concat([error_df, pd.DataFrame([new_row])], ignore_index=True)


#create a filename  with the current date and time  
filename = 'output/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_output.csv'
#write the output dataframe to a csv file
output_df.to_csv(filename, index=False)
#write the error dataframe to a csv file if it has more than one row
print(error_df.shape[0])
if len(error_df.index) > 1:
    error_filename = 'output/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_error.csv'
    error_df.to_csv(error_filename, index=False)
