fetch(
  "https://ais.usvisa-info.com/en-za/niv/schedule/64083789/appointment/days/101.json?appointments[expedite]=false",
  {
    headers: {
      accept: "application/json, text/javascript, */*; q=0.01",
      "accept-language": "en-GB,en;q=0.8",
      "if-none-match": 'W/"391fd92b097d9a07fed76e5979ee754d"',
      "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"macOS"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-origin",
      "sec-gpc": "1",
      "x-csrf-token":
        "cdgwW1Ca5bDVnHPBgAseo4zNNLRw3BpuGhNyJlyAX6vl64XCAgvAPq+adLQEMwhwgTUV3lUUss6X8r2tBx2VOg==",
      "x-requested-with": "XMLHttpRequest",
      cookie:
        "_yatri_session=D%2FRtfJpa4AIcVHftWYr4OfVvpnL3IGKg0qzTT5C5wPV9Bo2PrigZhiGs68zqjI2GdZ6qvyBrQskr3cu9kmY2RZJ0ZgKQg7yVS5aMHZQBnUUS2NsPKf7lipoiczhaXfjBA9TnCA%2FOvZUzUsTwVlsLKZ%2FQSYTW2JIu0bVJXv7IYnFNQlHj%2BfroqAJqUEpeLj%2FR%2BrmFX%2Fzr8MFjtGrw1QowUiKFGKKsCHHtMj2OGZ0zF7VkQyIV%2F7LfRcwq2ayiZE9oTnhIsP7GBKiBvaWF5u3plnNSXz78VxzpusUE6EmJQH3kVk3l6eCLVkToWC5zyKn0RafW6%2BWsnZF7GMtZdPyQ%2Bd%2FQ5%2Fa2FoztHyN4%2Fkc0ufu37vCpgCOzo3%2BaCwFgC0LGAqqZJkVbnpVS2i%2F5WgyP2U994UYaqsqCbPfqHNKZifOqQY5%2F5UeEcO8axeICUTSrzEcTT7Km9ROCbMT%2Br6RaVlCeV4hnO6WKoX6Tt1pdRE%2BuDfTPTIeZW06XSoiVA%2B3Zai501kRIBqrSMJ2M4PcNmo%2FupXm0jpRaoqmBnCQaHiOJqAAtcTLWr789nDEoMo7mbTY5s6buqAJI2nLRwrQhEyfSFi4vs%2BngBf4643sLYMJ2tiZUV5bFtzejSYmmOCDDhhBC3oFqXIn8ACRk621KMuuLlKOyVoHdBxp2aPdBV4J%2FjGYPj%2FMepUpVb9%2FBHf6kqDESMdrEyLhmo%2FcyKlvxKjCRLz8wD1W2FEbkIwRMvXua7Zq8Yu3NJsQgPwK4s5ozbgvz6lAEzfjQblYfWD54FMjE8Vzf9YxaltxWSi%2F4Vlp0P0fBtH3BgFqlMjTFTeHefJI%3D--2iEI8u3VGbKDY2OW--yuLPCsZwPFL4I5mTfXuVGg%3D%3D",
      Referer:
        "https://ais.usvisa-info.com/en-za/niv/schedule/64083789/appointment",
      "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    body: null,
    method: "GET",
  }
)
  .then((response) => console.log(response))
//   .then((data) => {
//     console.log("Appointment days data:", data);
//   })
//   .catch((error) => {
//     console.error("Error fetching appointment days:", error);
//   });
