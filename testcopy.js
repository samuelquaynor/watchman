const fs = require("fs").promises;
const path = require("path");
const { Builder, By, until } = require("selenium-webdriver");
const chrome = require("selenium-webdriver/chrome");
require("chromedriver");

async function loginAndGetAppointments(email, password) {
  let driver;

  try {
    const options = new chrome.Options();
    options.addArguments(
      "--headless",
      "--disable-gpu",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--window-size=1920,1080",
      "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    );

    options.setLoggingPrefs({ performance: "ALL" });
    options.addArguments("--enable-logging", "--v=1");

    driver = await new Builder()
      .forBrowser("chrome")
      .setChromeOptions(options)
      .build();

    const cookiesPath = path.join(__dirname, "cookies.json");
    let needLogin = true;

    try {
      const cookiesData = await fs.readFile(cookiesPath, "utf-8");
      const cookies = JSON.parse(cookiesData);
      await driver.get("https://ais.usvisa-info.com/en-za/niv");
      for (const cookie of cookies) {
        await driver.manage().addCookie(cookie);
      }

      await driver.get("https://ais.usvisa-info.com/en-za/niv/groups");
      needLogin = !(await driver.getCurrentUrl()).includes("/niv/groups");

      // await driver.get(
      //   "https://ais.usvisa-info.com/en-za/niv/schedule/64083789/payment"
      // );

      // const findTable = await driver.findElement(By.css("table.for-layout"));

      // console.log(`found table: ${findTable}`);

      // needLogin = false;
    } catch (error) {
      console.log("No valid cookies found, proceeding with login");
    }

    if (needLogin) {
      await driver.get("https://ais.usvisa-info.com/en-za/niv/users/sign_in");

      await driver.wait(until.elementLocated(By.id("user_email")), 20000);
      await driver.findElement(By.id("user_email")).sendKeys(email);
      await driver.findElement(By.id("user_password")).sendKeys(password);

      const checkbox = await driver.findElement(By.id("policy_confirmed"));
      await driver.executeScript("arguments[0].click();", checkbox);

      const submitButton = await driver.findElement(
        By.css("input[type='submit'][value='Sign In']")
      );
      await driver.executeScript("arguments[0].click();", submitButton);

      try {
        const errorElement = await driver.wait(
          until.elementLocated(By.css("p.error")),
          20000
        );
        const errorText = await errorElement.getText();
        if (errorText.includes("Invalid email or password")) {
          throw new Error("Invalid credentials provided");
        }
      } catch (error) {
        if (error.name === "TimeoutError") {
          // No error message found, continue with the flow
        } else {
          throw error; // Re-throw if it's the invalid credentials error
        }
      }

      await driver.wait(until.urlContains("/niv/groups/"), 20000);

      // Save cookies after successful login
      const cookies = await driver.manage().getCookies();
      await fs.writeFile(cookiesPath, JSON.stringify(cookies));
    }

    await driver.get(
      "https://ais.usvisa-info.com/en-za/niv/schedule/64083789/appointment"
    );

    // Wait for the page to load
    await driver.wait(until.elementLocated(By.css("body")), 10000);

    // Enable network interception
    await driver.executeScript("window.networkRequests = [];");
    await driver.executeScript(`
      var originalFetch = window.fetch;
      window.fetch = function() {
        return originalFetch.apply(this, arguments).then(function(response) {
          var clone = response.clone();
          clone.text().then(function(body) {
            window.networkRequests.push({
              url: response.url,
              body: body
            });
          });
          return response;
        });
      };
    `);

    // Trigger the appointment data request
    await driver.executeScript(`
      fetch("https://ais.usvisa-info.com/en-za/niv/schedule/64083789/appointment/days/101.json?appointments[expedite]=false", {
        headers: {
          "accept": "application/json, text/javascript, */*; q=0.01",
          "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
          "x-requested-with": "XMLHttpRequest"
        },
        method: "GET",
        credentials: "include"
      });
    `);

    // Wait for the request to complete
    await driver.sleep(5000);

    // Retrieve the intercepted requests
    const requests = await driver.executeScript(
      "return window.networkRequests;"
    );

    // Find the appointment data request
    const appointmentData = requests.find((req) =>
      req.url.includes("/appointment/days/101.json")
    );

    if (appointmentData) {
      console.log("Appointment data retrieved successfully");
      console.log("Response Body:", JSON.parse(appointmentData.body));
      // Process the appointment data as needed
    } else {
      console.log("Failed to retrieve appointment data");
    }
  } catch (error) {
    throw new Error(`Failed to retrieve appointments: ${error.message}`);
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}

async function main() {
  try {
    const email = "samwillsquaye@gmail.com"; // Replace with your actual email
    const password = "Millions$9913";
    if (!email || !password) {
      throw new Error(
        "Email and password must be provided as environment variables"
      );
    }
    const appointments = await loginAndGetAppointments(email, password);
    console.log("Available appointments:", appointments);
  } catch (error) {
    console.error("Error:", error.message);
    // Handle the error appropriately (e.g., send an alert, log to a service, etc.)
  }
}

main();
