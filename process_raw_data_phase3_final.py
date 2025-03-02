"""
Created on Fri Apr 23 12:39:25 2021

@author: Diogo
"""

# Clear the console and remove all variables present on the namespace. This is 
# useful to prevent Python from consuming more RAM each time I run the code.
try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass


import pandas as pd
from tqdm import tqdm


print("2 lengthy commands will follow, with respective progress bars:")


# Load data
underlying = pd.read_csv("Processed data/underlying.csv")
options = pd.read_csv("Processed data/options_phase2.csv")


# Remove options with Time_to_Maturity = 0
options = options[options["Time_to_Maturity"] != 0]

# Remove options with Option_Average_Price = 0. I don't know why I did this.
# If I had to do it again I would probably drop it because these options can 
# also be a source of information.
options = options[options["Option_Average_Price"] != 0]


# CREATE LIST WITH THE STANDARD DEVIATIONS THAT MATCH EACH OPTIONS' QUOTEDATE
# Total number of options
n_options = options.shape[0]

sigma_20_annualized = []
for index, row in tqdm(options.iterrows(), total = n_options):
    (sigma_20_annualized.append(float(underlying["Sigma_20_Days_Annualized"].
                                    loc[underlying["Date"] == row.QuoteDate])))
    
    
# Add sigma_20_annualized as a column in the options DF
options["Sigma_20_Days_Annualized"] = sigma_20_annualized

# Create list with the closing prices of the underlying that match each 
# option's QuoteDate
underlying_price = []
for index, row in tqdm(options.iterrows(), total = n_options):
    (underlying_price.append(float(underlying[" Close"].loc[underlying["Date"] 
                                                        == row.QuoteDate])))

# Add column of closing price of the underlying for each QuoteDate and drop 
# more unnecessary columns
options["Underlying_Price"] = underlying_price
options = options.drop(["expiration", "underlying_bid_eod",
                        "underlying_ask_eod"], axis = 1)

# Create csv file from the options df
options.to_csv('Processed data/options_phase3_final.csv', index = False)

