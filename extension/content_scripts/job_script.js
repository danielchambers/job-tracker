(function () {
  // Check if the extension root already exists
  if (document.getElementById("extension-root")) {
    return;
  }

  // Create a shadow root
  const extensionRoot = document.createElement("div");
  extensionRoot.id = "extension-root";
  document.body.insertBefore(extensionRoot, document.body.firstChild);
  const shadowRoot = extensionRoot.attachShadow({ mode: "closed" });

  // Create and inject CSS
  const style = document.createElement("style");
  style.textContent = `
    #extension-header {
      font-family: Arial, sans-serif;
      font-size: 14px;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      background-color: #f0f0f0;
      color: #333;
      padding: 10px;
      display: flex;
      justify-content: flex-start;
      align-items: center;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      z-index: 2147483647;
      box-sizing: border-box;
    }
    #extension-header > * {
      margin-right: 10px;
    }
    #extension-header button {
      font-family: inherit;
      font-size: inherit;
      padding: 5px 10px;
      background-color: #4CAF50;
      color: white;
      border: none;
      cursor: pointer;
      border-radius: 3px;
    }
    #extension-header select {
      font-family: inherit;
      font-size: inherit;
      padding: 5px;
      border: 1px solid #ccc;
      background-color: white;
      color: #333;
    }
    #message-container {
      font-family: inherit;
      font-size: inherit;
      margin-left: 10px;
      color: #ff0000;
    }
  `;
  shadowRoot.appendChild(style);

  const header = document.createElement("div");
  const saveButton = document.createElement("button");
  const messageContainer = document.createElement("span");
  const dropdown1 = document.createElement("select");
  const dropdown2 = document.createElement("select");
  
  header.id = "extension-header";
  saveButton.textContent = "Save";
  messageContainer.id = "message-container";
  dropdown1.innerHTML = '<option value="">Select Document</option>';
  dropdown2.innerHTML = '<option value="">Select Sheet</option>';

  // Function to populate dropdowns
  function populateDropdowns() {
    chrome.runtime.sendMessage({ action: "getDocuments" }, (response) => {
      if (chrome.runtime.lastError) {
        console.error("Error:", chrome.runtime.lastError);
        return;
      }
      if (response.error) {
        console.error("Error retrieving documents:", response.error);
        return;
      }
      const documents = response.documents || [];
      console.log("Retrieved documents:", JSON.stringify(documents));

      if (documents.length === 0) {
        return;
      }

      const groupedDocuments = documents.reduce((acc, doc) => {
        if (!acc[doc.title]) {
          acc[doc.title] = [];
        }
        acc[doc.title].push(doc);
        return acc;
      }, {});

      dropdown1.innerHTML = '<option value="">Select Document</option>';

      Object.keys(groupedDocuments).forEach((title) => {
        const option = document.createElement("option");
        option.value = title;
        option.textContent = title;
        dropdown1.appendChild(option);
      });

      dropdown1.addEventListener("change", (e) => {
        const selectedTitle = e.target.value;
        dropdown2.innerHTML = '<option value="">Select Sheet</option>';
        if (selectedTitle && groupedDocuments[selectedTitle]) {
          groupedDocuments[selectedTitle].forEach((doc) => {
            const option = document.createElement("option");
            option.value = JSON.stringify({ id: doc.id, sheet: doc.sheet });
            option.textContent = doc.sheet;
            dropdown2.appendChild(option);
          });
        }
      });
    });
  }

  function makePostRequest(documentId, sheetName) {
    const jobUrl = document.URL;
    const data = {
      job_url: jobUrl,
      document_id: documentId,
      sheet_name: sheetName,
    };

    chrome.runtime.sendMessage(
      {
        action: "addJob",
        data: data,
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error("Error:", chrome.runtime.lastError);
          messageContainer.textContent = "Error adding job. Please try again.";
          messageContainer.style.color = "#ff0000";
        } else {
          console.log("Response:", response);
          if (response.success) {
            messageContainer.textContent = response.message;
            messageContainer.style.color = "#4CAF50";
          } else {
            messageContainer.textContent =
              response.message || "Error adding job. Please try again.";
            messageContainer.style.color = "#ff0000";
          }
        }

        setTimeout(() => {
          messageContainer.textContent = "";
        }, 3000);
      }
    );
  }

  populateDropdowns();


  saveButton.onclick = () => {
    const selectedTitle = dropdown1.value;
    const selectedSheetValue = dropdown2.value;

    if (selectedTitle && selectedSheetValue) {
      const { id: documentId, sheet: sheetName } =
        JSON.parse(selectedSheetValue);
      makePostRequest(documentId, sheetName);
    } else {
      messageContainer.textContent =
        "Please make a selection in both dropdowns.";
      messageContainer.style.color = "#ff0000";

      setTimeout(() => {
        messageContainer.textContent = "";
      }, 3000);
    }
  };

  header.appendChild(saveButton);
  header.appendChild(dropdown1);
  header.appendChild(dropdown2);
  header.appendChild(messageContainer);
  shadowRoot.appendChild(header);
  document.body.style.paddingTop = extensionRoot.offsetHeight + 10 + "px";
})();
