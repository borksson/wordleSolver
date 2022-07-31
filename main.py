import json
import time
import Solver as solver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

with open('selectors.json', 'r') as file:
    SELECTORS = json.load(file)

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_experimental_option("excludeSwitches", ["enable-logging", "disable-default-apps"])

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get(SELECTORS["sites"]["WORDLE"])

instructions_close = driver.find_element(By.CSS_SELECTOR, SELECTORS["selectors"]["INSTRUCTIONS_CLOSE"])
instructions_close.click()

board = driver.find_element(By.CSS_SELECTOR, SELECTORS["selectors"]["BOARD"])

rows = board.find_elements(By.XPATH, "./*")

print("NUM ROWS: ", len(rows))

solver_obj = solver.Solver()

guess = "adieu"

for row in rows:
    print("GUESS :", guess)
    ActionChains(driver).send_keys(guess).key_down(Keys.ENTER).perform()
    time.sleep(2)
    children = row.find_elements(By.XPATH, "./*")
    key = []
    for i in range(len(children)):
        tile = children[i].find_element(By.XPATH, "./*")
        state = tile.get_attribute("data-state")
        if state == "absent":
            key.append('_')
        elif state == "correct":
            key.append(guess[i].upper())
        elif state == "present":
            key.append(guess[i])
    key = ''.join(key)
    if key == guess.upper():
        print("ANSWER: ", guess)
        break
    guess = [*solver.get_best_guesses(solver_obj.make_guess(guess, key), 1)[0]][0]


input("Press enter to quit.\n")

driver.quit()