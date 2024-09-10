from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

def exec_request(url, data, method, token):
  headers = {
    'Content-Type': 'application/json',
    'x-access-token': f'{token}'
  }

  if method.lower() == 'put':
    response = requests.put(url, json=data, headers=headers)
  elif method.lower() == 'get':
    response = requests.get(url, headers=headers)
  else:
    raise ValueError("Unsupported method: only 'put' and 'get' are supported")
  
  response.raise_for_status()

  try:
    return response.json()
  except requests.exceptions.JSONDecodeError:
    return response


def wait_for_element(driver, locator, timeout=60, poll_frequency=1, ignored_exceptions=None):
  if ignored_exceptions is None:
    ignored_exceptions = [NoSuchElementException, TimeoutException]

  wait = WebDriverWait(driver, timeout=timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
  element = wait.until(EC.presence_of_element_located(locator))
  return element

def convert_currency_to_int(currency_str):
  cleaned_str = currency_str.replace('$', '').replace(',', '')
  return float(cleaned_str)