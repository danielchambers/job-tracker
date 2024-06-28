let documents = [];

function saveOptions() {
  console.log("Saving documents:", documents);
  browser.storage.local.set({ documents }, function () {
    console.log("Documents saved successfully");
    // Immediately try to retrieve the documents
    browser.storage.local.get("documents", function (result) {
      console.log("Documents immediately after saving:", result.documents);
    });
  });
}

function restoreOptions() {
  browser.storage.local
    .get("documents")
    .then((result) => {
      documents = result.documents || [];
      console.log("Documents loaded:", documents);
      updateList();
    })
    .catch((error) => {
      console.error("Error loading documents:", error);
    });
}

function updateList() {
  const list = document.getElementById("docList");
  list.innerHTML = "";
  documents.forEach((doc, index) => {
    const li = document.createElement("li");
    li.textContent = `${doc.title} - ${doc.id} - ${doc.sheet}`;
    const buttonsDiv = document.createElement("div");
    buttonsDiv.className = "edit-delete-buttons";

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.onclick = () => editDocument(index);

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.onclick = () => deleteDocument(index);

    buttonsDiv.appendChild(editBtn);
    buttonsDiv.appendChild(deleteBtn);
    li.appendChild(buttonsDiv);
    list.appendChild(li);
  });
}

function addDocument() {
  const title = document.getElementById("docTitle").value;
  const id = document.getElementById("docId").value;
  const sheet = document.getElementById("sheetName").value;
  if (title && id && sheet) {
    documents.push({ title, id, sheet });
    saveOptions();
    updateList();
    clearForm();
  }
}

function editDocument(index) {
  const doc = documents[index];
  document.getElementById("docTitle").value = doc.title;
  document.getElementById("docId").value = doc.id;
  document.getElementById("sheetName").value = doc.sheet;
  documents.splice(index, 1);
  updateList();
}

function deleteDocument(index) {
  documents.splice(index, 1);
  saveOptions();
  updateList();
}

function clearForm() {
  document.getElementById("docTitle").value = "";
  document.getElementById("docId").value = "";
  document.getElementById("sheetName").value = "";
}

document.addEventListener("DOMContentLoaded", restoreOptions);
document.getElementById("saveBtn").addEventListener("click", addDocument);
