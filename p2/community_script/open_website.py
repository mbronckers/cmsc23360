# Edited by Max Bronckers

import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

WEBSITES = [
  "https://youtube.com",
  "https://yahoo.com",
  "https://facebook.com",
  "https://reddit.com",
  "https://netflix.com",
  "https://ebay.com",
  "https://instructure.com",
  "https://twitch.tv",
  "https://live.com",
  "https://stackoverflow.com",
  "https://linkedin.com",
  "https://irs.gov",
  "https://imdb.com",
  "https://nytimes.com",
  "https://cnn.com",
  "https://salesforce.com",
  "https://okta.com",
  "https://wikipedia.org",
  "https://imgur.com",
  "https://dropbox.com",
  "https://zillow.com",
  "https://etsy.com",
  "https://hulu.com",
  "https://quizlet.com",
  "https://homedepot.com"
]


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Open website in browser using Selenium')
  parser.add_argument('-i', action='store', dest='website', type=int, default="0",
                      help='Which website to open')
  args = parser.parse_args()

  options = Options()
  options.headless = True

  driver = webdriver.Firefox(options=options)
  driver.get(WEBSITES[args.website])
  driver.close()