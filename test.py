import pandas as pd
import gspread
import numpy as np

gc = gspread.oauth(
    credentials_filename='credentials.json',
    authorized_user_filename='authorized_user.json'
)

cm_package = gc.open('CM NSHIP PACKAGE INFORMATION 2023')
main_file = pd.DataFrame(cm_package.worksheet('MAIN FILE').get_all_records())
main_file_inbound = main_file['Inbound tracking'].to_list()

unreceived = pd.read_csv('unreceived.csv')

unreceived['Inbound tracking'] = unreceived['Inbound tracking'].str[1:]
unreceived['Outbound tracking'] = unreceived['Outbound tracking'].str[4:]

mascara = unreceived['Inbound tracking'].isin(['link to amazon', 'Tracking Available Soon']) |\
          pd.isna(unreceived['Inbound tracking'])

link = unreceived.loc[~mascara]

link_inbound = link['Inbound tracking'].to_list()

no_match = []
match = []
for i in main_file_inbound:
    if type(i) is not str:
        i = str(i)
    for i2 in link_inbound:
        if len(i) == len(i2):
            turn = 0
            different = False
            while turn < len(i):
                if i[turn] != i2[turn]:
                    different = True
                    break
                else:
                    turn += 1
            if not different:
                if i not in match:
                    match.append(i)

print('fin')
