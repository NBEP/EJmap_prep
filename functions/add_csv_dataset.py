# ---------------------------------------------------------------------------
# add_csv_dataset
# Last updated: 2022-04-19
# Authors: Mariel Sorlien
#
# Description:
# Helper functions to import and process csv datasets for ejmap_step2
# ---------------------------------------------------------------------------

import pandas as pd

# --------------------- add_csv_dataset -----------------------------
# Import csv, drop extra rows and columns, rename columns, save csv
# csv_input = input csv name and location
# metrics = column names for selected metrics (list)
# new_metrics = dictionary of metric name substitutes (dictionary; old: new)
# extra_columns = additional columns to keep
# states = list of states
# state_column = column in csv input with state names
# csv_output = output csv name and location


def add_csv_dataset(csv_input, metrics, new_metrics, extra_columns,
                    states, state_column, csv_output):
    print('Selecting columns')
    column_list = extra_columns + metrics
    print('Reading in csv')
    # Only imports selected columns (column_list)
    df = pd.read_csv(csv_input,
                     sep=",",
                     usecols=column_list)
    print('Filtering data for selected states')
    df = df[df[state_column].isin(states)]
    if new_metrics is not None:
        print('Renaming columns')
        df.rename(columns=new_metrics,
                  inplace=True)
    print('Saving file')
    df.to_csv(csv_output, index=False)

# --------------------- add_first_street_data -----------------------------
# Imports first street dataset, calculates average risk factor per census tract
# csv_input = input csv name and location
# metric = 'flood', 'heat'
# csv_output = output csv name and location


def add_first_street_data(csv_input, metric, csv_output):
    print('Reading in csv')
    df = pd.read_csv(csv_input,
                     sep=",")
    print('Calculating average ' + metric.lower() + ' risk')
    df[metric.upper()] = (df['count_' + metric.lower() + 'factor1'] +
                          2*df['count_' + metric.lower() + 'factor2'] +
                          3*df['count_' + metric.lower() + 'factor3'] +
                          4*df['count_' + metric.lower() + 'factor4'] +
                          5*df['count_' + metric.lower() + 'factor5'] +
                          6*df['count_' + metric.lower() + 'factor6'] +
                          7*df['count_' + metric.lower() + 'factor7'] +
                          8*df['count_' + metric.lower() + 'factor8'] +
                          9*df['count_' + metric.lower() + 'factor9'] +
                          10*df['count_' + metric.lower() + 'factor10']
                          )/df['count_property']
    print('Dropping extra columns')
    df = df[['fips', metric.upper()]]
    print('Renaming column')
    df.rename(columns={'fips': 'Tract_ID'},
              inplace=True)
    print('Saving file')
    df.to_csv(csv_output, index=False)
