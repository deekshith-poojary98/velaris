Feature: Login

Scenario: User logs in

  Given browser.open("/login")
  When browser.type("#username", "demo")
  Then browser.click("#submit")
