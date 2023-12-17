#Self fixing web automation for locators in rpaframework & Selenium (POC)
This POC attempts to create a new class based on Selenium which decorates the core element finder with a function that traps an ElementNotFound error and attempts to send the locator and the html to openai to get it to  return a good xpath locator, which it tests.

If the locator tests OK, then the automation script will continue from where the error occurred.

This was inspired by Krzysztof Karaszewski’s post on linkedin:
https://www.linkedin.com/feed/update/urn:li:activity:7130576929530810368/, 
where he produced the same thing in UiPath.

####Notes
The method to decorate/wrap the specific method in Selenium to achieve this
was hard to achieve as it took some research to try and establish what the base
method was. The actual wrapping is not as elegant as it could be, but it was
after many different attempts.

I also used the new robocorp libraries for python https://robocorp.com/docs/python to use the task decorator, log library and vault (local). I did this for Selenium being more accustomed to it than the Playwright based library in the new python framework.

If you wish to try this I recommend:
1. Have a robocorp account (free) even if you don't use orchestrator to store api
keys, as it is easy to implement a good local store of keys and credentials
2. Ensure you have the Robocorp extension for VS Code
3. Let the extension manage packages for you instead of working in venv's
4. I used local storage for my openai key following the convention for secrets
using a vault.json file and env.json. I had some difficulty with this because I
foolishly didn't let the extension or rcc set up my bot folder. There is a 
great paper on this here: 
https://forum.robocorp.com/t/using-robocorp-vault-in-local-development-run/598
It took me a few goes, but the key is to fetch the worksapce id from:
https://cloud.robocorp.com/personalsrn9u/development/settings and the 
Credential id from here https://cloud.robocorp.com/settings/access-credentials
(after viewing the token).

####Limitations:
* only wraps single find method, not tested with finding multiple elements
* doesn't handle locator aliases (in locators.json) but can be modified to do that
* it's not guaranteed the openai prompt will work for other pages, it had to be
tweaked quite a bit to get OpenAI to return just the xpath and not use the
wrong tag attributes (like class).
* it's just about a POC, it is not made for serious automation.