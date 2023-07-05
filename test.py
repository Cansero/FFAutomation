import pandas as pd
import gspread

gc = gspread.oauth(
    credentials_filename='credentials.json',
    authorized_user_filename='authorized_user.json'
)


def new_packages():
    cm_package = gc.open('CM NSHIP PACKAGE INFORMATION 2023')
    main_file = pd.DataFrame(cm_package.worksheet('MAIN FILE').get_all_records())
    main_file['Inbound tracking'] = main_file['Inbound tracking'].astype(str)

    unreceived = pd.read_csv('CSV/unreceived.csv')
    unreceived = unreceived.loc[:, 'Status':'Postal Code']

    unreceived['Inbound tracking'] = unreceived['Inbound tracking'].str[1:]
    unreceived['Outbound tracking'] = unreceived['Outbound tracking'].str[4:]

    mascara = unreceived['Inbound tracking'].isin(['link to amazon', 'Tracking Available Soon']) | \
              pd.isna(unreceived['Inbound tracking'])

    link = unreceived.loc[~mascara]

    mascara1 = link['Inbound tracking'].isin(main_file['Inbound tracking'])

    compare = link.loc[~mascara1]

    print('fin')


def asins():
    master_file = gc.open('MASTER FILE NUEVO')
    master_file = pd.DataFrame(master_file.worksheet('DATA').get_all_records())
    master_file['ASIN\n0'] = master_file['ASIN\n0'].astype(str)

    asins_manual = gc.open('UNRECEIVED CA')
    asins_manual = pd.DataFrame(asins_manual.worksheet('UNRECEIVED CA').get_all_records())

    unreceived = pd.read_csv('CSV/unreceived.csv')
    unreceived = unreceived.loc[:, ['ASIN', 'Country']]
    unreceived = unreceived.fillna(value={'Country': 'China'})
    unreceived['Country'] = unreceived['Country'].apply(lambda x: x.upper())
    unreceived['ASIN'] = unreceived['ASIN'].astype(str)

    coo = pd.read_csv('CSV/UNRECEIVED CA - COO.csv')

    mascara = unreceived['ASIN'].isin(master_file['ASIN\n0'])

    unreceived = unreceived.loc[~mascara]


    test = pd.read_csv('CSV/test.csv')
    mascara_test = unreceived['ASIN'].isin(test['ASIN'])

    test1 = unreceived.loc[~mascara_test]

    print('fin')


if __name__ == '__main__':
    asins()
