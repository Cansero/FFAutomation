from time import sleep

import gspread
import pyautogui
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import main
import references

options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')

gc = gspread.oauth(
    credentials_filename='credentials.json',
    authorized_user_filename='authorized_user.json'
)


def log_in(driver):
    while True:
        try:
            driver.find_element(by=By.XPATH, value='/html/body/div[3]/form/div/div[1]/input').send_keys(references.user)
            driver.find_element(by=By.XPATH, value='/html/body/div[3]/form/div/div[2]/input').\
                send_keys(references.password)
            driver.find_element(by=By.XPATH, value='/html/body/div[3]/form/div/div[3]/button').click()
            return

        except NoSuchElementException:
            sleep(2)
            driver.refresh()


def search_tracking(driver, tracking):
    while True:
        try:
            trkng_box = driver.find_element(by=By.NAME, value='search_tracking_number')
            trkng_box.clear()
            trkng_box.send_keys(tracking)
            trkng_box.send_keys(Keys.RETURN)
            return
        except NoSuchElementException:
            sleep(2)
            driver.refresh()


def detect_state(driver, place):
    state = driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[2]"
                                                   "//a[contains(@class,'active')]".format(place)).text
    return state


def is_hold(driver, place):
    try:
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[3]"
                                               "//*[contains(text(),'HOLD REQUEST')]".format(place))
        return True
    except NoSuchElementException:
        return False


def place_as(state, driver, place):
    try:
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[2]"
                                               "//*[contains(text(),'{}')]".format(place, state)).click()
    except NoSuchElementException:
        print("Can't place as {}".format(state))


def place_nship(driver, place, nship):
    try:
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[4]/div/a[1]".format(place)).click()
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[4]/div/span//input".format(place)).clear()
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[4]/div/span//input".format(place)).send_keys(nship)
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[4]/div/span//button".format(place)).click()
    except NoSuchElementException:
        print("Can't place nship")


def has_outbound(driver, place):
    try:
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[3]"
                                               "//*[contains(text(),'label')]".format(place))
        return True
    except NoSuchElementException:
        return False


def find_match(driver, place, tracking):
    try:
        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[3]"
                                               "//*[contains(text(),'{}')]".format(place, tracking))
        return True
    except NoSuchElementException:
        return False


def accept_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass


def match_finder(search, list_to_match, container):
    n = 0
    while n + 2 < len(search):
        result = search[n] + " " + search[n + 1] + " " + search[n + 2]
        result = result.upper()
        if result in list_to_match and result not in container:
            container.append(result)
        n += 1

    n = 0
    while n + 1 < len(search):
        result = search[n] + " " + search[n + 1]
        result = result.upper()
        if result in list_to_match and result not in container:
            container.append(result)
        n += 1

    n = 0
    while n < len(search):
        result = search[n]
        result = result.upper()
        if result in list_to_match and result not in container:
            container.append(result)
        n += 1


def receiving(list_from_program, time_to_sleep):

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(references.url)

    log_in(driver)

    holds, not_found, repeated, problems = [], [], [], []

    for tracking, nship in list_from_program:

        search_tracking(driver, tracking)

        results = len(driver.find_elements(by=By.XPATH, value="//tbody/tr"))

        if results == 0:
            not_found.append(tracking)

        row = 1
        times_appear = 0
        while row <= results:
            if find_match(driver, row, tracking) is True:
                state = detect_state(driver, row)
                hold = is_hold(driver, row)

                place_as('Received', driver, row)
                place_nship(driver, row, nship)

                if hold:
                    place_as('Hold', driver, row)
                    holds.append(tracking)

                if state in ['Problems for Forwarder', 'Problems for Client']:
                    place_as(state, driver, row)

                times_appear += 1
                row += 1

            else:
                row += 1

        if times_appear > 1:
            repeated.append(tracking)

        sleep(time_to_sleep)

    driver.quit()
    return repeated, holds, problems, not_found


def pre_manifest(list_from_program, time_to_sleep):

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(references.url)

    log_in(driver)

    state = []
    place = 0
    for outbound in list_from_program:
        place += 1
        row = 1
        search_tracking(driver, outbound)

        results = len(driver.find_elements(by=By.XPATH, value="//tbody/tr"))
        matches = len(driver.find_elements(by=By.XPATH, value="//tbody/tr/td[3]"
                                                              "//*[contains(text(),'{}')]".format(outbound)))

        if not results:
            state.append(f'{place}.- {outbound} - Not found')

        elif matches > 1:
            state.append(f'{place}.- {outbound} - Repeated')

        elif results and not matches:
            state.append(f'{place}.- {outbound} - HOLD')

        else:
            while row <= results:
                if find_match(driver, row, outbound) is True:
                    active_button = detect_state(driver, row)

                    if active_button not in ['Unreceived', 'Received']:
                        state.append(f'{place}.- {outbound} - {active_button}')
                    else:
                        state.append(f'{place}.- {outbound} - Pre-manifested')

                    place_as('Pre-Manifest', driver, row)
                    accept_alert(driver)

                    row += 1

                else:
                    row += 1

        sleep(time_to_sleep)

    driver.quit()
    return state


def print_label(list_from_program):

    ff_file = gc.open('FF File').sheet1.col_values(1)
    ff_file_nship = gc.open('FF File').sheet1.col_values(2)

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(references.url)

    log_in(driver)

    messages = []
    place = 0
    for tracking in list_from_program:
        place += 1
        indices = []

        if tracking[0] == 'N':
            for i, label in enumerate(ff_file_nship):
                if tracking[-12:] == label[-12:]:
                    indices.append(i)
        else:
            for i, label in enumerate(ff_file):
                if tracking[-12:] == label[-12:]:
                    indices.append(i)

        if not len(indices):
            messages.append(f'{place}.- {tracking} - Not found')

        elif len(indices) > 1:
            messages.append(f'{place}.- {tracking} - Combined')

        else:
            tracking = ff_file[indices[0]][1:]

            search_tracking(driver, tracking)

            results = len(driver.find_elements(by=By.XPATH, value="//tbody/tr"))
            row = 1

            original_window = driver.current_window_handle

            while row <= results:
                if find_match(driver, row, tracking) is True:
                    if not is_hold(driver, row):
                        driver.implicitly_wait(10)
                        driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[3]"
                                                               "//*[contains(text(),'label')]".format(row)).click()
                        for window_andle in driver.window_handles:
                            if window_andle != original_window:
                                driver.switch_to.window(window_andle)
                                break
                        driver.execute_script("window.print();")
                        sleep(2)
                        pyautogui.press('enter')
                        sleep(0.5)
                        driver.close()
                        driver.switch_to.window(original_window)
                        outbound = driver.find_element(by=By.XPATH, value="//tbody/tr[{}]/td[3]"
                                                                          "//*[contains(@href,'canadapost.ca')]"
                                                       .format(row)).text
                        messages.append(f'{place}.- {tracking} - {outbound}')

                        driver.implicitly_wait(0)

                    else:
                        messages.append(f'{place}.- {tracking} - Hold')

                    row += 1

                else:
                    row += 1

    driver.quit()
    return messages


def codes(list_from_program):

    cells_values = []

    item_desc = gc.open("CODES FINDER CA").worksheet("MASTER").col_values(1)

    driver = webdriver.Chrome()
    for asin in list_from_program:
        matches = []
        subtitle = None
        amz_url = "https://www.amazon.ca/dp/{}?psc=1".format(asin)

        driver.get(amz_url)

        try:
            title = driver.find_element(By.ID, "productTitle").text
        except NoSuchElementException:
            break
        try:
            subtitle = driver.find_element(By.ID, "productSubtitle").text
        except NoSuchElementException:
            pass

        title = title.replace(",", " ").replace("-", " ").replace(".", " ").split()
        if subtitle:
            subtitle = subtitle.split()
            if subtitle[0].upper() == "PAPERBACK":
                matches.append("PAPERBACK BOOK")
            if subtitle[0].upper() == "HARDCOVER":
                matches.append("HARDCOVER BOOK")

        match_finder(title, item_desc, matches)

        sel = main.OptionSelection(labels=matches, desc=item_desc)
        sel.exec()
        cells_values.append(sel.get_selection)

    driver.quit()
    return cells_values
