import json

import scrapy
import traceback
import argparse
import requests
from scrapy import Selector
from datetime import datetime
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, JavascriptException
from selenium.webdriver.support import expected_conditions as EC
from ProgressiveMotorcycleBot.spiders.utils import convert_currency_to_int, exec_request, wait_for_element

from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By

def logging(driver):
  email = 'sewellinsurance'
  password = 'Sewell2$'
  login_url = 'https://www.foragentsonly.com/login/'
  driver.get(login_url)
  email_input = wait_for_element(driver, (By.XPATH, '//input[@data-at="external-login-input-textbox-user-id-agent"]'))
  email_input.send_keys(email)
  driver.find_element(By.XPATH, '//input[@data-at="external-login-input-textbox-password"]').send_keys(password)
  driver.find_element(By.XPATH, '//input[@class="blueBtn base-btn loginButton"]').click()

  time.sleep(3)

def existing_quote(driver):
  driver.find_element(By.XPATH, '//*[@id="existingQuote"]').click()
  driver.find_element(By.XPATH, '//*[@id="LstNm"]').send_keys('User')
  driver.find_element(By.XPATH, '//*[@id="EQStart"]').click()
  time.sleep(3)

  # driver.find_element(By.XPATH, '//*[@id="products_MC"]').click()
  # driver.find_element(By.XPATH, '//*[@id="quoteActionSelectButton"]').click()
  # time.sleep(5)

  td_text = 'User, Test'
  td_element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, f"//a[text()='{td_text}']"))
  )
  driver.find_element(By.XPATH, '//*[@id="quoteResultsTable"]/tbody/tr[2]/td[1]/p/a').click()
  print('New window found', driver.window_handles)
  new_window = driver.window_handles[-1]
  driver.switch_to.window(new_window)
  new_window_url = driver.current_url
  print('New URL:', new_window_url)
  time.sleep(5)
  # products button
  driver.find_element(By.XPATH, '//button[@class="btn i-right save-data ng-star-inserted"]').click()
  time.sleep(2)



def new_quote(driver, body):
  print('in new quote')
  new_quote_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="newQuote"]')))
  print('new quote btn found')
  driver.execute_script("arguments[0].click();", new_quote_btn)
  print('New Quote BTN clicked')
  driver.find_element(By.XPATH, '//select[@id="QuoteStateList"]').click()
  print('state opened')
  for option in driver.find_elements(By.XPATH, '//select[@id="QuoteStateList"]/option'):
      print('options!', option.text, body.get('state') )
      if option.text == body.get('state'):
          print('state matched!', option.text)
          option.click()
          break
  print('state clicked')
  time.sleep(2)
  product_button = wait_for_element(driver, (By.XPATH, '//*[@id="selectProductButton"]'))
  product_button.click()
  print('product btn clicked')
  time.sleep(2)
  # Select Motorcycle/Atv
  driver.find_element(By.CSS_SELECTOR, 'a[data-at="new-quote-product-selector-button-MC"]').click()
  print('motorcycle selection')
  driver.find_element(By.CSS_SELECTOR, 'input.ppButton#quoteActionSelectButton').click()
  print('New window found', driver.window_handles)
  new_window = driver.window_handles[-1]
  driver.switch_to.window(new_window)
  new_window_url = driver.current_url
  print('New URL:', new_window_url)


def named_insured(driver, body):
  # first name
  first_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_FirstName"]')))
  print('first name found')
  first_name.send_keys(body.get('first_name'))

  # middle
  if body.get('middle_name'):
      driver.find_element(By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_MiddleInitial"]').send_keys(body.get('middle_name'))

  # last
  driver.find_element(By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_LastName"]').send_keys(body.get('last_name'))

  # suffix
  if body.get('suffix'):
      suffix = driver.find_element(By.CSS_SELECTOR, 'select[id="NamedInsured_Embedded_Questions_List_Suffix"]')
      driver.execute_script("arguments[0].scrollIntoView(true);", suffix)
      suffix.click()
      for option in driver.find_elements(By.CSS_SELECTOR, 'select[id="NamedInsured_Embedded_Questions_List_Suffix"]>option'):
          if option.text == body.get('suffix'):
              option.click()
              break

  # gender
  gender = driver.find_element(By.CSS_SELECTOR, 'select[id="NamedInsured_Embedded_Questions_List_Gender"]')
  driver.execute_script("arguments[0].scrollIntoView(true);", gender)
  gender.click()
  for option in driver.find_elements(By.CSS_SELECTOR, 'select[id="NamedInsured_Embedded_Questions_List_Gender"]>option'):
      if option.text == body.get('gender'):
          option.click()
          break

  # email
  driver.find_element(By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_PrimaryEmailAddress"]').send_keys(body.get('email'))

  # mailing address line 1
  driver.find_element(By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_MailingAddress"]').send_keys(body.get('mailing_address_line_1'))

  # city
  driver.find_element(By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_City"]').send_keys(body.get('city'))

  # zip
  driver.find_element(By.CSS_SELECTOR, 'input[id="NamedInsured_Embedded_Questions_List_ZipCode"]').send_keys(body.get('zip'))

  # moved in the last two months
  moved = driver.find_element(By.CSS_SELECTOR, '#NamedInsured_Embedded_Questions_List_RecentlyMoved')
  driver.execute_script("arguments[0].scrollIntoView(true);", moved)
  gender.click()
  for option in driver.find_elements(By.CSS_SELECTOR, '#NamedInsured_Embedded_Questions_List_RecentlyMoved>option'):
      if option.text == 'No':
          option.click()
          break

  # disclosure
  disclosure_exists = _is_exist_selector(driver=driver, xpath='//select[@id="NamedInsured_Embedded_Questions_List_DisclosureProvided"]')
  if disclosure_exists:
      disclosure = driver.find_element(By.XPATH, '//select[@id="NamedInsured_Embedded_Questions_List_DisclosureProvided"]')
      driver.execute_script("arguments[0].scrollIntoView(true);", disclosure)
      disclosure.click()

      for option in driver.find_elements(By.XPATH, '//select[@id="NamedInsured_Embedded_Questions_List_DisclosureProvided"]/option'):
          if option.text == body.get('disclosure'):
              option.click()
              break

  # Date of Birth
  driver.find_element(By.XPATH, '//date-input[@autocompleteyrtype="DateOfBirth"]//input[@id="NamedInsured_Embedded_Questions_List_DateOfBirth"]').send_keys(body.get('date_of_birth'))

  # products button
  driver.find_element(By.XPATH, '//button[@class="btn i-right save-data ng-star-inserted"]').click()
  time.sleep(2)


def motorcycles(driver, body):
  # Select Policy Effective Date
  # date_label = driver.find_element(By.XPATH, '//label[@id="PolicyEffectiveDate_Label"]').click()
  effective_date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ProductsMC_Embedded_Questions_List_PolicyEffectiveDate"]')))
  print('effective date found')
  effective_date.send_keys(body.get('effective_date'))

  for i, motorcycle in enumerate(body.get('motorcycles', [])):
      if i != 0:
          # add new button
          test_element = driver.find_element(By.XPATH, '//*[@id="MC"]/div[2]/add-entity-main/div/div/div')
          print('tester', test_element)
          effective_date = driver.find_element(By.XPATH, '//*[@id="MC"]/div[1]/question-box/div/question/div[2]/datepicker-combo-input/div/date-input/mat-form-field/div[1]')
          driver.execute_script("arguments[0].scrollIntoView(true);", effective_date)
          time.sleep(2)
          print('add new button')
          # add_new_button = driver.find_element(By.XPATH, '//*[@id="MC"]/div[2]/add-entity-main/div/div/div')
          test_element.click()
          time.sleep(3)

      # vehicle_types
      driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_TypeCode"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_TypeCode"]/option'):
          if option.text == 'Motorcycle/Trike':
              option.click()
              break

      time.sleep(2)
      # vin 
      # driver.find_element(By.XPATH, '//*[@id="ProductsMC_Vehicles_List_0_Embedded_Questions_List_Vin"]').send_keys(motorcycle.get('vin'))
      # time.sleep(2)
      # driver.find_element(By.XPATH, '//*[@id="MC"]/div[2]/question-table/question-row[2]/question/div[2]/vin-input/div/button').click()
      # time.sleep(5)
      # year
      driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Year"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Year"]/option'):
          if option.text == motorcycle.get('year'):
              option.click()
              break

      time.sleep(2)
      # make
      driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Make"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Make"]//option'):
          if option.text == motorcycle.get('make'):
              option.click()
              break

      time.sleep(2)
      # model
      driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Model"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Model"]//option'):
          if option.text == motorcycle.get('model'):
              option.click()
              break

      time.sleep(2)
      # cc_size
      if motorcycle.get('engine_size') and motorcycle.get('engine_size') != 300:
        try:
            driver.find_element(By.XPATH, f'//input[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_EngineSize"]').clear()
            driver.find_element(By.XPATH, f'//input[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_EngineSize"]').send_keys(motorcycle.get('engine_size'))
        except JavascriptException as e:
            print(f"Element is not interactable: {e}")

      # is_this_vehicle_trike
      try:
        driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_IsTrike"]').click()
        for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_IsTrike"]/option'):
            if option.text == motorcycle.get('is_this_vehicle_trike'):
                option.click()
                break
      except:
        pass
      time.sleep(2)

      # purchase year
      if motorcycle.get('purchase_year'):
          print('in purchase year')
          try:
              driver.find_element(By.XPATH, f'//*[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_PurchaseYear"]').click()
              for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_PurchaseYear"]/option'):
                  if option.text == motorcycle.get('purchase_year'):
                      option.click()
                      break
          except:
              pass

      time.sleep(2)
      # primary_vehicle_use
      try:
          driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_VehicleUse"]').click()
          for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_VehicleUse"]/option'):
              if option.text == motorcycle.get('primary_vehicle_use'):
                  option.click()
                  break
          time.sleep(2)
          if motorcycle.get('primary_vehicle_use') == 'Off-Road Use':
              driver.find_element(By.XPATH, f'//*[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_VehiclePrimaryUse"]').click()
              for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_VehiclePrimaryUse"]/option'):
                  if option.text == motorcycle.get('off_road_use'):
                      option.click()
                      break
          if motorcycle.get('primary_vehicle_use') in ['On-Road', 'On-Road/Off-Road']:
              print('in the second')
              driver.find_element(By.XPATH, f'//*[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_AnnualMileage"]').send_keys(motorcycle.get('annual_miles_ridden'))
      except:
          pass

      time.sleep(2)
      # modified_frame_turbo   
      try:
          driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Modification"]').click()
          for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_Modification"]/option'):
              if option.text == motorcycle.get('modified_frame_turbo'):
                  option.click()
                  break
      except:
          pass

      time.sleep(2)
      # lo_jack
      # try:
      #     driver.find_element(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_HomingDevice"]').send_keys('No')
      #     for option in driver.find_elements(By.XPATH, f'//select[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_HomingDevice"]/option'):
      #         if option.text == motorcycle.get('lo_jack'):
      #             option.click()
      #             break
      # except:
      #     pass

      # anti-lock brakes
      try:
          anti_lock_el = driver.find_element(By.XPATH, f'//*[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_AntilockBrakes"]')
          print('lock el', anti_lock_el)
          anti_lock_el.click()
          for option in driver.find_elements(By.XPATH, f'//*[@id="ProductsMC_Vehicles_List_{i}_Embedded_Questions_List_AntilockBrakes"]/option'):
              if option.text == motorcycle.get('anti_lock_brakes'):
                  option.click()
                  break
      except:
          pass
      time.sleep(2)


def household_members(driver, body):
  print('in household')
  for i, drvr in enumerate(body.get('drivers')):
      print('in for loop', i)
      if i != 0:
          # add new button
          add_btn = driver.find_element(By.XPATH, '/html/body/my-app/div/main/div/ng-component/div/add-entity-main/div/div/div')
          scroll_el = driver.find_element(By.XPATH, '//*[@id="People_Drivers_List_0_Embedded_Questions_List_FirstName"]')
          driver.execute_script("arguments[0].scrollIntoView(true);", scroll_el)
          time.sleep(2)
          # add_new_button = driver.find_element(By.XPATH, '//*[@id="MC"]/div[2]/add-entity-main/div/div/div')
          add_btn.click()
          print('add new button clicked')
          time.sleep(2)

          driver.find_element(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_FirstName"]').send_keys(drvr.get('first_name'))
          driver.find_element(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_LastName"]').send_keys(drvr.get('last_name'))
          driver.find_element(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_DateOfBirth"]').send_keys(drvr.get('date_of_birth'))
          # relationship
          relationship = wait_for_element(driver, (By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_Relationship"]'))
          relationship.click()
          for option in driver.find_elements(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_Relationship"]/option'):
              if option.text == drvr.get('relationship'):
                  option.click()
                  break

          time.sleep(2)
          # gender
          gender = wait_for_element(driver, (By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_Gender"]'))
          gender.click()
          for option in driver.find_elements(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_Gender"]/option'):
              if option.text == drvr.get('gender'):
                  option.click()
                  break

          time.sleep(2)
      # marital status
      marital_status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//select[@id="People_Drivers_List_{i}_Embedded_Questions_List_MaritalStatus"]')))
      print('marital status found')
      driver.execute_script("arguments[0].click();", marital_status)

      for option in driver.find_elements(By.XPATH, f'//select[@id="People_Drivers_List_{i}_Embedded_Questions_List_MaritalStatus"]/option'):
          if option.text == drvr.get('marital_status'):
              option.click()
              break
      print('selected marital')
      time.sleep(2)

      # highest level of education
      driver.find_element(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_HighestLevelOfEducation"]').click()
      for option in driver.find_elements(By.XPATH, f'//*[@id="People_Drivers_List_{i}_Embedded_Questions_List_HighestLevelOfEducation"]/option'):
          if option.text == drvr.get('highest_education'):
              option.click()
              break

      time.sleep(2)
      print('selected ed')
      # driver license status
      driver.find_element(By.XPATH, f'//select[@id="People_Drivers_List_{i}_Embedded_Questions_List_LicenseStatus"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="People_Drivers_List_{i}_Embedded_Questions_List_LicenseStatus"]/option'):
          if option.text == drvr.get('driver_license_status'):
              option.click()
              break

      time.sleep(2)
      print('selected license')
      # years licensed
      # years_licensed = _is_exist_selector(driver, xpath=f'//input[@id="People_Drivers_List_{i}_Embedded_Questions_List_InputDriverYearsLicensed"]')
      # if years_licensed:
      #     driver.find_element(By.XPATH, f'//input[@id="People_Drivers_List_{i}_Embedded_Questions_List_InputDriverYearsLicensed"]').send_keys(drvr.get('years_licensed'))
      #     time.sleep(2)
      # print('selected years lic')
      # motorcycle endorsement
      driver.find_element(By.XPATH, f'//select[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_ValidMotorcycleEndorsement"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_ValidMotorcycleEndorsement"]/option'):
          if option.text == drvr.get('motorcycle_endorsement'):
              option.click()
              break

      time.sleep(2)
      print('selected endorse')
      # years riding experience
      driver.find_element(By.XPATH, f'//input[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_YearsExperience"]').send_keys(drvr.get('years_riding_experience'))
      time.sleep(2)

      # approved safety course
      driver.find_element(By.XPATH, f'//select[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_SafetyCourseTaken"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_SafetyCourseTaken"]/option'):
          if option.text == drvr.get('approved_safety_course'):
              option.click()
              break

      time.sleep(2)
      print('selected safety')
      # how often ride
      driver.find_element(By.XPATH, f'//select[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_RideFrequency"]').click()
      for option in driver.find_elements(By.XPATH, f'//select[@id="People_Drivers_List_{i}_ProductSpecificInformation_List_0_Embedded_Questions_List_RideFrequency"]/option'):
          if option.text == drvr.get('how_often_ride'):
              option.click()
              break

      time.sleep(2)
      print('selected ride')

def additional_details(driver, body):
  # prior insurance
  prior_insurance = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="AdditionalDetails_ProductSpecificInformation_List_0_Embedded_Questions_List_InsuranceToday"]')))
  print('prior insurance found')
  driver.execute_script("arguments[0].click();", prior_insurance)

  for option in driver.find_elements(By.XPATH, '//*[@id="AdditionalDetails_ProductSpecificInformation_List_0_Embedded_Questions_List_InsuranceToday"]/option'):
      if option.text == body.get('has_prior_insurance'):
          option.click()
          break
  time.sleep(2)
  print('prior clicked', body.get('has_prior_insurance'))
  if body.get('has_prior_insurance') == 'Yes':
      # prior carrier
      driver.find_element(By.XPATH, '//*[@id="AdditionalDetails_ProductSpecificInformation_List_0_Embedded_Questions_List_RecentAutoInsuranceCompanyDisplay"]').click()
      for option in driver.find_elements(By.XPATH, '//*[@id="AdditionalDetails_ProductSpecificInformation_List_0_Embedded_Questions_List_RecentAutoInsuranceCompanyDisplay"]/option'):
          if option.text == body.get('prior_carrier'):
              option.click()
              break
  
      # prior expiration date
      time.sleep(2)
      print('ex date', body.get('prior_expiration_date'))
      ex_date = driver.find_element(By.XPATH, '//*[@id="AdditionalDetails_ProductSpecificInformation_List_0_Embedded_Questions_List_PreviousInsuranceExpirationDate"]')
      ex_date.clear()
      ex_date.send_keys(body.get('prior_expiration_date'))
  print('prior carrier and date clicked', body.get('prior_carrier'), body.get('prior_expiration_date'))
  # primary residence
  primary_residence = wait_for_element(driver, (By.XPATH, '//select[@id="AdditionalDetails_Embedded_Questions_List_PrimaryResidenceDisplay"]'))
  primary_residence.click()
  for option in driver.find_elements(By.XPATH, '//select[@id="AdditionalDetails_Embedded_Questions_List_PrimaryResidenceDisplay"]/option'):
      if option.text == body.get('primary_residence'):
          option.click()
          break
  time.sleep(2)
  print('primary clicked', body.get('primary_residence'))
  # no additional risk
  driver.find_element(By.XPATH, '//*[@id="AdditionalDetails_Embedded_Questions_List_MultiPolInd"]').click()
  time.sleep(2)
  print('poll clicked')

def coverages(driver, body):
    for i, motorcycle in enumerate(body.get('motorcycles', [])):
      if i == 0:
        # bodily injury
        bodily_injury = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_BIPDGP"]')))
        print('bodily injury found')
        driver.execute_script("arguments[0].click();", bodily_injury)
        for option in driver.find_elements(By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_BIPDGP"]/option'):
            if option.text == body.get('bodily_injury'):
                option.click()
                break
        time.sleep(2)
        # uninsured motorist
        uninsured_motorist = wait_for_element(driver, (By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_UMBI"]'))
        uninsured_motorist.click()
        for option in driver.find_elements(By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_UMBI"]/option'):
            if option.text == body.get('uninsured_motorist'):
                option.click()
                break
        time.sleep(2)
        # underinsured motorist
        underinsured_motorist = wait_for_element(driver, (By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_UIM"]'))
        underinsured_motorist.click()
        for option in driver.find_elements(By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_UIM"]/option'):
            if option.text == body.get('underinsured_motorist'):
                option.click()
                break
        time.sleep(2)
        # medical payment
        medical_payment = wait_for_element(driver, (By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_MEDPAY"]'))
        medical_payment.click()
        for option in driver.find_elements(By.XPATH, '//*[@id="CoveragesMC_Vehicles_List_0_Embedded_Questions_List_MEDPAY"]/option'):
            if option.text == body.get('medical_payment'):
                option.click()
                break
        time.sleep(2)
      # collision deductible
      coll_deductible = wait_for_element(driver, (By.XPATH, f'//*[@id="CoveragesMC_Vehicles_List_{i}_Embedded_Questions_List_COMP"]'))
      coll_deductible.click()
      for option in driver.find_elements(By.XPATH, f'//*[@id="CoveragesMC_Vehicles_List_{i}_Embedded_Questions_List_COMP"]/option'):
          if option.text == body.get('comp_deductible'):
              option.click()
              break
      time.sleep(2)
      # comp deductible
      comp_deducltible = wait_for_element(driver, (By.XPATH, f'//*[@id="CoveragesMC_Vehicles_List_{i}_Embedded_Questions_List_COLL"]'))
      comp_deducltible.click()
      for option in driver.find_elements(By.XPATH, f'//*[@id="CoveragesMC_Vehicles_List_{i}_Embedded_Questions_List_COLL"]/option'):
          if option.text == body.get('coll_deductible'):
              option.click()
              break
      time.sleep(2)
      # recalculate button
      try:
          recal_btn = driver.find_element(By.XPATH, '/html/body/my-app/div/iaq-footer/footer/div/div[1]/button')
          recal_btn.click()
      except NoSuchElementException:
          print('No re-calculate button found')
      time.sleep(2)

def _is_exist_selector(driver, css='', xpath='', timeout=7):
  try:
    if css:
        WebDriverWait(driver, timeout=timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    elif xpath:
        WebDriverWait(driver, timeout=timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
    return True  # Success

  except NoSuchElementException:
    return False

  except TimeoutException:
    return False

  except ElementNotInteractableException:
    return False

  except ElementClickInterceptedException:
    return False

  except StaleElementReferenceException:
    return False




def run_bot(body): 
  print("Starting Progressive Bot")
  time.sleep(5)
  response = {}
  auth_token = body['token']
  print(auth_token)
  org_id = body['orgId']
  print('org', org_id)
  job_id = body['id']
  print('id', job_id)
  data = body['data']
  print('data!', data)
  # Production settings
  options = webdriver.ChromeOptions()
  options.binary_location = '/opt/chrome/chrome'
  options.add_argument("--headless=new")
  options.add_argument('--no-sandbox')
  options.add_argument("--disable-gpu")
  options.add_argument("--window-size=1280x1696")
  options.add_argument("--single-process")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-dev-tools")
  options.add_argument("--no-zygote")
  options.add_argument(f"--user-data-dir={mkdtemp()}")
  options.add_argument(f"--data-path={mkdtemp()}")
  options.add_argument(f"--disk-cache-dir={mkdtemp()}")
  options.add_argument("--remote-debugging-port=9222")
  service = Service(executable_path="/opt/chromedriver/chromedriver")
  driver = webdriver.Chrome(service=service, options=options)

  # Local settings
  # options = Options()
  # service = webdriver.ChromeService('/usr/local/bin/chromedriver')
  # options.binary_location = '	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  # options.add_argument('--no-sandbox')
  # options.add_argument("--disable-gpu")
  # options.add_argument("--window-size=1280x1696")
  # options.add_argument("--single-process")
  # options.add_argument("--disable-dev-shm-usage")
  # options.add_argument("--disable-dev-tools")
  # options.add_argument("--no-zygote")
  # options.add_argument(f"--user-data-dir={mkdtemp()}")
  # options.add_argument(f"--data-path={mkdtemp()}")
  # options.add_argument(f"--disk-cache-dir={mkdtemp()}")
  # options.add_argument("--remote-debugging-port=9222")
  # service = Service()
  # driver = webdriver.Chrome(service=service, options=options)

  try:
    # Update job status to running
    status_update = {
      'kind':'status',
      'status':'Running',
    }
    print("Updating Bot Status to Running")
    # exec_request(f"https://workflows-api.xilo.io/api/org/{org_id}/rate-jobs/update-status/{job_id}", status_update, 'put', auth_token)
    # exec_request(f"http://host.docker.internal:3333/api/org/{org_id}/rate-jobs/update-status/{job_id}", status_update, 'put', auth_token)

    # login
    print("Logging in")
    logging(driver)

    # Start a new quote
    print("Starting New Quote")
    new_quote(driver, body)
    # existing_quote(driver)
    starting_quote_url = driver.current_url
    print('New URL and handles:', starting_quote_url, driver.window_handles)
    time.sleep(7)

    # Fill the form
    print("Filling Named Insured")
    named_insured(driver, body)
    print("Filling Motorcycles")
    motorcycles(driver, body)

    # Household members button
    driver.find_element(By.XPATH, '//span[text()="HOUSEHOLD MEMBERS"]/parent::button').click()
    time.sleep(3)

    print("Filling Household Members")
    household_members(driver, body)

    # additional details button
    driver.find_element(By.XPATH, '//span[text()="ADDITIONAL DETAILS"]/parent::button').click()
    time.sleep(3)

    print('Filling Additional Details')
    additional_details(driver, body)
    # converges button
    driver.find_element(By.XPATH, '//span[text()="COVERAGES/BILL PLANS"]/parent::button').click()
    time.sleep(3)

    print('Filling Coverages')
    coverages(driver, body)
    time.sleep(3)

    try:
        close_button = wait_for_element(driver, (By.XPATH, '//button[text()="Close"]'))
        close_button.click()

    except:
        pass

    # Get all payment options
    time.sleep(2)
    print('Generating quote info')
    data          = {}
    quote = driver.find_element(By.XPATH, '/html/body/my-app/div/iaq-footer/footer/div/div[1]/div[1]/div/div[2]').text
    rawQuoteNum = driver.find_element(By.XPATH, '//*[@id="product_tab_MC"]/div/div[2]/span').text
    quote_number = rawQuoteNum.split(":")[1].strip()

    driver.find_element(By.XPATH, '//*[@id="MC"]/coverages-au-sl/bill-plan/div/div/div[1]/button').click()
    data['eftPaymentPlan'] = driver.find_element(By.XPATH, '//*[@id="P3400Y_span-period-text"]/money-content[2]/span').text
    data['eftPaymentTotal'] = driver.find_element(By.XPATH, '//*[@id="P3400Y_span-period-text"]/money-content[3]/span').text

    data['automaticCardPaymentPlan'] = driver.find_element(By.XPATH, '//*[@id="P3400C_span-period-text"]/money-content[2]/span').text
    data['automaticCardPaymentTotal'] = driver.find_element(By.XPATH, '//*[@id="P3400C_span-period-text"]/money-content[3]/span').text
    data['mailPayPaymentPlan'] = driver.find_element(By.XPATH, '//*[@id="P3400N_span-period-text"]/money-content[2]/span').text
    data['mailPayPaymentTotal'] = driver.find_element(By.XPATH, '//*[@id="P3400N_span-period-text"]/money-content[3]/span').text
    # quote = '$2938.52'
    response['quotePrice']      = convert_currency_to_int(quote)
    response['quotePriceRaw']   = quote
    response['quoteNumber']     = quote_number
    response['data']            = data

    driver.quit()
    print(f"Bot Completed Successfully + r: {response}")
    return response
  except:
    print(traceback.format_exc())
    driver.quit()
    return traceback.format_exc()
    

  driver.quit()

class MotorcyleBotSpider(scrapy.Spider):
    name = 'Motorcyle_Bot'

    # run_bot({
    #     "createdById": 4329,
    #     "createdByRole": "agent",
    #     "type": "Quote",
    #     "status": "Created",
    #     "requestId": 93,
    #     "orgId": 354,
    #     "clientId": 739213,
    #     "insuranceDataId": 11687,
    #     "submissionId": 'null',
    #     "carrierId": 1,
    #     "lob": "motorcycle",
    #     "usState": "CA",
    #     "execMode": "live",
    #     "createdAt": "2024-07-23T18:10:25.250Z",
    #     "updatedById": 4329,
    #     "updatedByRole": "agent",
    #     "updatedAt": "2024-07-23T18:10:25.250Z",
    #     "deletedById": 'null',
    #     "deletedByRole": 'null',
    #     "error": 'null',
    #     "resultedAt": 'null',
    #     "id": 125,
    #     "deletedAt": 'null',
    #     "first_name": "Test",
    #     "last_name": "User",
    #     "gender": "Male",
    #     "email": "test@sewell.com",
    #     "date_of_birth": "12161993",
    #     "primary_residence": "Own Home/Condo",
    #     "effective_date": "09292024",
    #     "how_long_at_residence": "1-2 years",
    #     "disclosure": "Yes",
    #     "motorcycles": [
    #         {
    #             "vehicle_types": "Motorcycle",
    #             "vin": "5HD1FC4157Y653840",
    #             "year": "2016",
    #             "make": "Yamaha",
    #             "model": "TW200",
    #             "is_this_vehicle_trike": "No",
    #             "primary_vehicle_use": "On-Road",
    #             "annual_miles_ridden": 2500,
    #             "modified_frame_turbo": "No",
    #             "lo_jack": "Yes",
    #             "anti_lock_brakes": "No",
    #             "purchase_year": "2016",
    #             "engine_size": 300
    #         },
    #         {
    #             "vehicle_types": "Motorcycle",
    #             "vin": "1HD1PG8448Y958361",
    #             "year": "2017",
    #             "make": "Honda",
    #             "model": "CB500X",
    #             "is_this_vehicle_trike": "No",
    #             "primary_vehicle_use": "On-Road",
    #             "annual_miles_ridden": 2500,
    #             "modified_frame_turbo": "No",
    #             "lo_jack": "Yes",
    #             "anti_lock_brakes": "No",
    #             "purchase_year": "2016"
    #         }
    #     ],
    #     "drivers": [
    #         {
    #             "marital_status": "Married",
    #             "driver_license_status": "Valid",
    #             "years_licensed": 5,
    #             "motorcycle_endorsement": "No",
    #             "years_riding_experience": 5,
    #             "approved_safety_course": "Yes",
    #             "date_of_birth": "12161993",
    #             "how_often_ride": "Weekly",
    #             "highest_education": "College degree",
    #             "relationship": "Other",
    #             "coll_deductible": "$250 Actual Cash Value",
    #             "comp_deductible": "$250 Actual Cash Value",
    #             "first_name": "Test",
    #             "last_name": "User",
    #             "gender": "Male"
    #         },
    #         {
    #             "marital_status": "Married",
    #             "driver_license_status": "Valid",
    #             "years_licensed": 5,
    #             "motorcycle_endorsement": "No",
    #             "years_riding_experience": 5,
    #             "approved_safety_course": "Yes",
    #             "date_of_birth": "12161994",
    #             "how_often_ride": "Weekly",
    #             "highest_education": "College degree",
    #             "relationship": "Spouse",
    #             "coll_deductible": "$250 Actual Cash Value",
    #             "comp_deductible": "$250 Actual Cash Value",
    #             "first_name": "Test",
    #             "last_name": "User",
    #             "gender": "Female"
    #         }
    #     ],
    #     "data": {
    #         "Drivers": [
    #             {
    #                 "BirthDt": "1993-12-16T00:00:00.000Z",
    #                 "GenderCd": "M",
    #                 "LastName": "User",
    #                 "FirstName": "Test",
    #                 "BirthDtDay": 16,
    #                 "BirthDtYear": 1993,
    #                 "BirthDtMonth": 12,
    #                 "MaritalStatus": "S",
    #                 "DriverRelationshipToApplicantCd": "IN"
    #             },
    #             {
    #                 "BirthDt": "1994-12-16T00:00:00.000Z",
    #                 "GenderCd": "F",
    #                 "LastName": "User",
    #                 "FirstName": "Test",
    #                 "BirthDtDay": 16,
    #                 "BirthDtYear": 1993,
    #                 "BirthDtMonth": 12,
    #                 "MaritalStatus": "M",
    #                 "DriverRelationshipToApplicantCd": "SP"
    #             }
    #         ],
    #         "Insured": [
    #             {
    #                 "id": 1,
    #                 "Addr": {
    #                     "City": "Tuscon",
    #                     "Addr1": "3115 N Fairview Ave",
    #                     "PostalCode": "85705",
    #                     "StreetName": "N Fairview Ave",
    #                     "FullAddress": "3115 N Fairview Ave, Tuscon, AZ 85705, USA",
    #                     "StateProvCd": "AZ",
    #                     "StreetNumber": 3115
    #                 },
    #                 "Email": "test@sewell.com",
    #                 "BirthDt": "1993-12-16T00:00:00.000Z",
    #                 "Insured": "Insured-1",
    #                 "FullName": "Test User",
    #                 "GenderCd": "M",
    #                 "LastName": "User",
    #                 "FirstName": "Test",
    #                 "BirthDtDay": 16,
    #                 "BirthDtYear": 1993,
    #                 "InsuredRole": "FNI",
    #                 "BirthDtMonth": 12,
    #                 "MaritalStatus": "S",
    #                 "CellPhoneNumber": "+1-302-6075612",
    #                 "HomePhoneNumber": "+1-302-6075612",
    #                 "CellPhoneNumberPrefix": "607",
    #                 "CellPhoneNumberSuffix": "5612",
    #                 "HomePhoneNumberPrefix": "607",
    #                 "HomePhoneNumberSuffix": "5612",
    #                 "CellPhoneNumberAreaCode": "302",
    #                 "HomePhoneNumberAreaCode": "302"
    #             }
    #         ],
    #         "Location": {
    #             "City": "Tuscon",
    #             "Addr1": "3115 N Fairview Ave",
    #             "PostalCode": "85705",
    #             "StreetName": "N Fairview Ave",
    #             "FullAddress": "3115 N Fairview Ave, Tuscon, AZ 85705, USA",
    #             "StateProvCd": "AZ",
    #             "StreetNumber": 3115
    #         },
    #         "Vehicles": [
    #             {
    #                 "id": 1,
    #                 "VehicleRef": "Vehicle-1",
    #                 "LocationRef": "Location-1",
    #                 "BodilyInjury": {
    #                     "CoverageCd": "BI",
    #                     "BIPerOccLimit": "300000",
    #                     "BIPerPersonLimit": "100000"
    #                 },
    #                 "VehicleUseCd": "PL",
    #                 "CollDeductible": "500",
    #                 "CompDeductible": "500",
    #                 "DistanceOneWay": 1,
    #                 "RatedDriverRef": "Driver-1",
    #                 "UninsuredMotorist": {
    #                     "CoverageCd": "UM",
    #                     "BIPerOccLimit": "300000",
    #                     "BIPerPersonLimit": "100000"
    #                 },
    #                 "CollDeductibleAmount": 500,
    #                 "CompDeductibleAmount": 500,
    #                 "UnderInsuredMotorist": {
    #                     "CoverageCd": "UNDUM",
    #                     "BIPerOccLimit": "300000",
    #                     "BIPerPersonLimit": "100000"
    #                 },
    #                 "EstimatedAnnualDistance": 10000
    #             }
    #         ],
    #         "Motorcycles": [
    #             {
    #                 "VIN": "5HD1FC4157Y653840",
    #                 "Model": "Xv700",
    #                 "ModelYear": "2016",
    #                 "LojackDevice": "1",
    #                 "Manufacturer": "Yamaha",
    #                 "MotorcycleUse": "PL",
    #                 "EstimatedAnnualDistance": 2500
    #             },
    #             {
    #                 "VIN": "1HD1PG8448Y958361",
    #                 "Model": "Xv700",
    #                 "ModelYear": "2016",
    #                 "LojackDevice": "1",
    #                 "Manufacturer": "Yamaha",
    #                 "MotorcycleUse": "DW",
    #                 "EstimatedAnnualDistance": 2500
    #             }
    #         ],
    #         "RatingState": "CA",
    #         "CustomFields": {
    #             "AMS360": {
    #                 "CrossReference": [
    #                     {
    #                         "CrossReferenceType": "X-Reference",
    #                         "CrossReferenceValue": "User, Test"
    #                     }
    #                 ]
    #             }
    #         },
    #         "AutoPersPolicy": {
    #             "RenewalTerm": "6",
    #             "DesiredPolicy": {
    #                 "BodilyInjury": "100/300",
    #                 "UninsuredMotorist": "100/300",
    #                 "UnderInsuredMotorist": "100/300"
    #             },
    #             "EffectiveDate": "2024-07-24T00:00:00.000Z",
    #             "PaymentPlanCd": "MO",
    #             "MethodPaymentCd": "CreditCard",
    #             "AttachmentTypeCd": "1",
    #             "EffectiveDateDay": 24,
    #             "EffectiveDateYear": 2024,
    #             "EffectiveDateMonth": 7,
    #             "PersApplicationInfo": {
    #                 "ResidenceTypeCd": "DW",
    #                 "ResidenceOwnedRentedCd": "OWNED"
    #             }
    #         },
    #         "MailingAddress": {
    #             "id": 1,
    #             "City": "San Diego",
    #             "Addr1": "3650 Fallon Circle",
    #             "County": "San Diego County",
    #             "PostalCode": "92130",
    #             "StreetName": "Fallon Circle",
    #             "FullAddress": "3650 Fallon Cir, San Diego, CA 92130, USA",
    #             "LocationRef": "Location-1",
    #             "StateProvCd": "CA",
    #             "StreetNumber": 3650
    #         },
    #         "MotorcyclePersPolicy": {
    #             "RenewalTerm": "6",
    #             "PaymentPlanCd": "FL",
    #             "PolicyStatusCd": "NBS",
    #             "MethodPaymentCd": "CreditCard",
    #             "AttachmentTypeCd": "1",
    #             "EffectiveDate": "2024-07-29T00:00:00.000Z"
    #         },
    #         "TransactionRequestDt": "2024-06-29T00:00:00.000Z"
    #     },
    #     "has_prior_insurance": "No",
    #     "bodily_injury": "25/50/15",
    #     "uninsured_motorist": "25/50",
    #     "underinsured_motorist": "25/50",
    #     "medical_payment": "$5,000 Per Person",
    #     "mailing_address_line_1": "3115 N Fairview Ave",
    #     "city": "Tuscon",
    #     "state": "Arizona",
    #     "zip": "85705",
    #     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjo5MjYsInR5cGUiOiJhZG1pbiIsImNvbXBhbnlJZCI6MzU0LCJ1c2VybmFtZSI6ImFkbWluKzM1NEB4aWxvLmlvIiwiY29tcGFueVVzZXJJZCI6MzU0LCJ3b3JrZmxvd3NBY2NvdW50SWQiOjIwNn0sImlhdCI6MTcyMTc0NzY3MSwiZXhwIjoxNzIyMzUyNDcxfQ.nSyjmhlUA5n-D5-GPieMBSzRA6gJupWGQlTaUTzwgnQ"
    # })