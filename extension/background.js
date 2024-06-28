chrome.runtime.onInstalled.addListener(() => {
  // Initialize storage here if needed
  chrome.storage.local.set({ initialKey: "initialValue" }, () => {
    console.log("Storage initialized");
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    console.log("Tab updated:", tab.url);
    if (
      tab.url.includes("bamboohr.com") ||
      tab.url.includes("greenhouse.io") ||
      tab.url.includes("lever.co") ||
      tab.url.includes("smartrecruiters.com")
    ) {
      console.log("Matching URL detected, injecting content script");
      chrome.tabs.executeScript(
        tabId,
        {
          file: "content_scripts/job_script.js",
        },
        () => {
          if (chrome.runtime.lastError) {
            console.error(
              "Error injecting content script:",
              chrome.runtime.lastError
            );
          } else {
            console.log("Content script injected successfully");
          }
        }
      );
    }
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Background script received message:", message);

  if (message.action === "contentScriptLoaded") {
    console.log("Content script loaded in tab:", sender.tab.id);
    sendResponse({ received: true });
  }

  if (message.action === "getDocuments") {
    chrome.storage.local.get("documents", (result) => {
      if (chrome.runtime.lastError) {
        console.error(
          "Background script error retrieving documents:",
          chrome.runtime.lastError
        );
        sendResponse({ error: chrome.runtime.lastError.message });
      } else {
        console.log("Background script retrieved documents:", result.documents);
        sendResponse({ documents: result.documents || [] });
      }
    });
    return true; // Indicates we will send a response asynchronously
  }

  if (message.action === "addJob") {
    fetch("http://localhost:5000/jobs/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message.data),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        console.log("Success:", result);
        sendResponse({ success: true, message: result.message });
      })
      .catch((error) => {
        console.error("Error:", error);
        sendResponse({
          success: false,
          message: `Error adding job: ${error.message}. Please try again.`,
        });
      });
    return true; // Indicates we will send a response asynchronously
  }
});
