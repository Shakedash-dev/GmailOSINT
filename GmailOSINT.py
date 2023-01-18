# Name: GmailOSINT.py
# Author: Shakedash
# Description: Recieves a phone number or a gmail address and returns it's GAIA ID, name of the person and places he reviewed (and time taken).
# Date: 18.1.2023

# Imports.
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from time import sleep
from re import findall
import argparse
import sys

# Constants.
DEFAULT_SLEEP_TIME = 10
LOGIN_URL = "https://accounts.google.com/AccountChooser/signinchooser?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&flowName=GlifWebSignIn&flowEntry=AccountChooser"
REVIEWS_URL = "https://www.google.com/maps/contrib/{0}/reviews"

FORGOT_PASS_XPATH = '//*[@id="forgotPassword"]/div/button'
IDENTIFIER_UNKNOWN_XPATH = '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[2]/div[2]/div'
GAIA_ID_SCRIPT_XPATH = "/html/head/script[1]"
SUBMIT_IDENT_XPATH = '//*[@id="identifierNext"]/div/button'
INPUT_BOX_XPATH = '//*[@id="identifierId"]'
CHOOSE_AUTH_METHOD_XPATH = '//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul'
ADDRESS_IN_MAPS_XPATH = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[5]/div[2]/div[{0}]/div/div[3]/div[2]/div[2]/div[1]/div/div[2]/span[1]'
BUSINESS_IN_MAPS_XPATH = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[5]/div[2]/div[{0}]/div/div[3]/div[2]/div[2]/div[1]/div/div[1]/span'
REVIEW_TIME_IN_MAPS_XPATH = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[5]/div[2]/div[{0}]/div/div[3]/div[4]/div[1]/span[3]'
FULL_NAME_XPATH = (
    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div[2]/h1'
)

# Globals.
sleep_time = DEFAULT_SLEEP_TIME

# This function checks if one of the elements it recieves exists.
def CheckPageLoaded(driver, elements):

    # Check if page is loaded <sleep_time> times.
    for i in range(sleep_time):
        sleep(1)
        not_found_elements_counter = 0
        for element in elements:
            try:
                driver.find_element(By.XPATH, element)
            except:
                not_found_elements_counter += 1

        # If one of the elements the function is looking for exists, it probebly means the page is loaded
        # (or loaded enough to continue running).
        if not_found_elements_counter != len(elements):

            # Just return the execution to the original function.
            return True

        # If the loop is ending and the function didn't find any elements, it probebly means the page is not loaded.
        if i == sleep_time - 1:
            return False


# Prints the error message to screen, closes the driver, and exits.
def exit_peacefully(driver, message):
    print(message)
    driver.close()
    sys.exit(1)


# Initializing argparse with sleep and identifier arguments.
def argpars_init():
    global sleep_time
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "Identifier_Id",
        help="The identifier you want to search the GAIA ID by.\nCan be phone number or gmail address.",
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        help="Number of seconds to sleep between actions. If internet connection is poor, increase this argument.",
    )
    args = parser.parse_args()
    if args.sleep:
        sleep_time = args.sleep
    return args.Identifier_Id


# Find the GAIA ID inside the page.
def FindGAIAID(driver):

    # Get the GAIA ID out of the response.
    script_content = driver.find_element(By.XPATH, GAIA_ID_SCRIPT_XPATH).get_attribute(
        "innerHTML"
    )
    gaia_id = findall("\d{21}", script_content)

    # If GAIA ID found.
    if gaia_id != []:
        return gaia_id[0]
    else:
        print("No GAIA ID found for the current user.")


# Recieves GAIA ID and returns the person's name.
def GetNameByGAIAID(driver, gaia_id):
    driver.get(REVIEWS_URL.format(gaia_id))

    if not CheckPageLoaded(driver, [FULL_NAME_XPATH]):
        exit_peacefully(
            driver, "Poor internet connection...\nPlease use --sleep 20 (or higher)"
        )
    full_name = driver.find_element(By.XPATH, FULL_NAME_XPATH).get_attribute(
        "innerHTML"
    )
    return full_name


# GetAdressOfReviews() must be called after GetNameByGAIAID(), because it doe's not change the URL to the needed URL as GetNameByGAIAID() already doe's that.
# It returns a list of the location the account reviewed on.
def GetAdressOfReviews(driver):
    addresses = []
    more_reviews = True
    c = 1

    # Wait a bit for the page to load.
    CheckPageLoaded(driver, [ADDRESS_IN_MAPS_XPATH.format(1)])

    # Keep iterating on reviews untill finished.
    while more_reviews:
        try:
            address = driver.find_element(
                By.XPATH, ADDRESS_IN_MAPS_XPATH.format(str(c))
            ).get_attribute("innerHTML")

            # Sometimes businesses don't have a location to them so at least we can use the business name
            if address == "":
                address = driver.find_element(
                    By.XPATH, BUSINESS_IN_MAPS_XPATH.format(str(c))
                ).get_attribute("innerHTML")
            review_time = driver.find_element(
                By.XPATH, REVIEW_TIME_IN_MAPS_XPATH.format(str(c))
            ).get_attribute("innerHTML")
            addresses.append((address, review_time))
        except:
            more_reviews = False
        c += 2  # The XPATH changes by the count of 2 (for each review) for some reason.
    return addresses


def main():
    gaia_id = ""  # Init.
    Identifier_Id = argpars_init()

    driver = uc.Chrome(use_subprocess=True)
    # driver.maximize_window()

    driver.get(LOGIN_URL)
    driver.refresh()

    # Insert identifier.
    driver.find_element(By.XPATH, INPUT_BOX_XPATH).send_keys(Identifier_Id)

    # Submit.
    driver.find_element(By.XPATH, SUBMIT_IDENT_XPATH).click()

    # Check if page is loaded and proceed if so.
    if not CheckPageLoaded(driver, [FORGOT_PASS_XPATH, IDENTIFIER_UNKNOWN_XPATH]):
        exit_peacefully(
            driver, "Poor internet connection...\nPlease use --sleep 20 (or higher)"
        )

    # Check if a user exists for the given identifier.
    userexists = True
    try:
        driver.find_element(
            By.XPATH, IDENTIFIER_UNKNOWN_XPATH
        )  # If no error = unknown user.
        userexists = False
    except:
        pass

    if not userexists:
        exit_peacefully(
            driver,
            f"A Gmail account doe's not exists for identifier {Identifier_Id}",
        )

    # The try\except are for a wierd bug that sometimes happen.
    try:
        # Click forgot password.
        driver.find_element(By.XPATH, FORGOT_PASS_XPATH).click()
    except:
        sleep(1)

        # Click forgot password again.
        driver.find_element(By.XPATH, FORGOT_PASS_XPATH).click()

    # Need some loading time.
    sleep(sleep_time / 2)

    # Check if page is loaded and proceed if so.
    if not CheckPageLoaded(driver, [CHOOSE_AUTH_METHOD_XPATH]):

        # Check if the GAIA ID exists because in some cases there isn't a CHOOSE_AUTH_METHOD_XPATH element,
        # but still the GAIA ID can be found.
        gaia_id = FindGAIAID(driver)
        exit_peacefully(
            driver,
            "Poor internet connection...\nUsing --sleep 20 (or higher) might help",
        )

    # Find GAIA ID.
    gaia_id = FindGAIAID(driver)
    print(f"GAIA ID: {gaia_id}")

    # Get the full name of the owner of the gmail account.
    print(f"Full Name: {GetNameByGAIAID(driver, gaia_id)}")

    c = 1
    for address in GetAdressOfReviews(driver):
        print(f"Address {c}: {address[0]}")
        print(f"Time Taken {c}: {address[1]}\n")
        c += 1

    # Close the browser peacefully.
    driver.close()


if __name__ == "__main__":
    main()
