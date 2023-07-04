import pandas as pd
import gspread

gc = gspread.oauth(
    credentials_filename='credentials.json',
    authorized_user_filename='authorized_user.json'
)

cm_package = gc.open('CM NSHIP PACKAGE INFORMATION 2023')
main_file = pd.DataFrame(cm_package.worksheet('MAIN FILE').get_all_records())


unreceived = pd.read_csv('unreceived.csv')

unreceived['Inbound tracking'] = unreceived['Inbound tracking'].str[1:]
unreceived['Outbound tracking'] = unreceived['Outbound tracking'].str[4:]

mascara = unreceived['Inbound tracking'].isin(['link to amazon', 'Tracking Available Soon']) |\
          pd.isna(unreceived['Inbound tracking'])

link = unreceived.loc[~mascara]

print(link.shape)

mascara1 = link['Inbound tracking'].isin(main_file['Inbound tracking'])

compare = link.loc[~mascara1]

print(compare.shape)

print(main_file.shape)

print('fin')
