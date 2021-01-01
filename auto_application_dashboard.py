# README
# ----------------------- #
# The goal is to update an online dashboard with the latest enrollment numbers for summer camp.
# The dashboard displays cumulative enrollment on each day so far of the year.

# This script ingests a csv with camper enrollment data retrieved from a data management system (which as no API).
# The data is processed to fix a few type or name errors.
# A pivot table is created to count the number of campers who have cumulatively enrolled in each session so far.
# Finally, a connection is made to the online dashboard in Google Sheets and the data is updated.
# ----------------------- #

import pandas as pd
import datetime as dt
from gspread_pandas import Spread

# LOAD DATA
# ----------------------- #
file_name = '1_1_2021_13_0_53.csv'
file_path = f'C:\\Users\\avery\\Dropbox\\Data Analysis\\Databases\\Camper_Tracking_2021\\{file_name}'
full_df = pd.read_csv(file_path, index_col='PersonID')

# PROCESS DATA
# ----------------------- #
#  Change data type to datetime.
full_df['Application Date'] = pd.to_datetime(full_df['Application Date'])

# Fill empty enrolled sessions with applied sessions
full_df['Enrolled Sessions'] = full_df['Enrolled Sessions'].fillna(full_df['Applied Sessions'])

# Select subset to get only data we care about.
data_list = ['Full Name', 'Application Date', 'Enrolled Sessions', 'Gender']
df_sorted = full_df[data_list]

# Sort by application date
df_sorted = df_sorted.sort_values('Application Date', ascending=True)

# Change any early application dates to '9/15/2020'
early_app_condition = df_sorted['Application Date'] < '2020-09-15'
df_sorted.loc[early_app_condition, 'Application Date'] = '2020-09-15 00:00:00'

# Reconvert application date to datetime - otherwise will fail to join later.
df_sorted['Application Date'] = pd.to_datetime(df_sorted['Application Date'])

# Explicitly remap expedition sessions
exp_remap_dict = {'Western Expedition': 'EXP',
                  'Blue Ridge 1': 'EXP',
                  'Blue Ridge 2': 'EXP',
                  'Blue Ridge 3': 'EXP',
                  'Outer Banks 1': 'EXP',
                  'Outer Banks 2': 'EXP',
                  'Leadership in Training (LIT) 1': 'EXP',
                  'Leadership in Training (LIT) 2': 'EXP',
                  'Mountain Biking 2- Base Camp Expedition': 'EXP',
                  'Mountain Biking 1- Base Camp Expedition and Session 2': 'Session 2',
                  'Session 2 and Rock Climbing 1- Base Camp Expedition': 'Session 2',
                  'Session 3 and Circumnavigate GRP 2- Base Camp Expedition': 'Session 3',
                  'Session 2 and Session 4': 'Session 4',
                  'Rock Climbing 2- Base Camp Expedition and Session 3': 'Session 3',
                  'Session 2 and Mountain Biking 1- Base Camp Expedition': 'Session 2',
                  'Session 3 and Rock Climbing 2- Base Camp Expedition': 'Session 3'}

df_remapped = df_sorted.replace(exp_remap_dict)


# BUILD SESSION GUARDRAIL
# ----------------------- #
# Unique to 2021, camp has more sessions than usual including unique combinations we don't care about here.
# We want remapped values only. If the above remapping fails, the shape of the dataframe will have too many columns.
# We don't want to accidentally replace data in the dashboard with these bogus columns. Instead, we want an error.
# Throw an error if the data contains a value we haven't yet remapped.

# Create list of acceptable sessions
clean_session_list = ['EXP', 'Session 1', 'Session 2', 'Session 3', 'Session 4', 'Session 5', 'Session 6']

# Count records that match an acceptable session
remapped_count = df_remapped['Enrolled Sessions'].isin(clean_session_list).sum()

# Count all records
total_row_count = df_remapped['Enrolled Sessions'].count()

# Calculate the difference
difference = total_row_count - remapped_count

# If the difference != 0, print the values so we can see what incorrect value came through
if difference != 0:
    print(df_remapped['Enrolled Sessions'].value_counts())
else:
    pass

# Throw error if difference != 0
assert difference == 0, "Non-acceptable sessions passed"


# CREATE PIVOT TABLE
# ----------------------- #
# Pivot to count apps per date
pivot_count_df = pd.pivot_table(df_remapped,
                                values='Full Name',
                                index=['Application Date'],
                                columns=['Enrolled Sessions'],
                                aggfunc='count',
                                fill_value=0)

# Calculate cumulative sum of the pivot table rows down each column
pivot_cum_df = pivot_count_df.cumsum(axis=0)


# COMPLETE DATES
# ----------------------- #
# The above dataframe omits dates where no applications have been received.
# Instead of blanks, we want to see every single date.
# To accomplish this, we need to create a dataframe with the full dates and merge them together.

# Place key inside a string to use as date start and end.
start_string = "2020-08-01"
end_string = "2021-07-31"

# Convert strings to datetime type
start_date = dt.datetime.strptime(start_string, '%Y-%m-%d')
end_date = dt.datetime.strptime(end_string, '%Y-%m-%d')

# Generate temporary dataframe with time series.
date_series = pd.date_range(start=start_date, end=end_date)
date_df = pd.DataFrame(date_series)
date_df.columns = ['Standard Date']

# Merge dates dataframe with pivot table dataframe
joined_df = pd.merge_ordered(pivot_cum_df, date_df, left_on='Application Date', right_on='Standard Date', how='right')


# FILL NULLS
# ----------------------- #
# On each day where no campers have applied at all, the dataframe currently contains an entire row of nulls.
# We actually want the same number as the day before, so we'll back fill nulls.

# We don't want to back fill for dates before registration opened
# First, create a condition for values before registration date
before_registration = joined_df['Standard Date'] < '2020-09-14'

# Set values before registration date to zero
joined_df.loc[before_registration, clean_session_list] = 0

# Back fill na values after registration
joined_df.fillna(method='bfill', inplace=True)

# Set index to 'Standard Date'
joined_df.set_index('Standard Date', inplace=True)


# UPDATE DASHBOARD
# ----------------------- #

# Connect to Google Sheet
app_dashboard = Spread('Daily Application Dashboard')

# Update 'YTD' sheet with the results from the joined_df
app_dashboard.df_to_sheet(joined_df, index=False, sheet='YTD', start='B1', merge_headers=True)
