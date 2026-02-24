const API_BASE = ""; // same origin when served from Flask

const gmailInput = document.getElementById("gmail");
const appPasswordInput = document.getElementById("appPassword");
const subjectInput = document.getElementById("subject");
const bodyInput = document.getElementById("body");
const recipientsInput = document.getElementById("recipients");
const recipientCountEl = document.getElementById("recipientCount");
const sendAllBtn = document.getElementById("sendAll");
const statusEl = document.getElementById("status");
const resultsCard = document.getElementById("resultsCard");
const resultsList = document.getElementById("resultsList");

function parseRecipients(text) {
  return text
    .split(/\n/)
    .map((line) => line.trim().toLowerCase())
    .filter((email) => email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
}

function updateRecipientCount() {
  const list = parseRecipients(recipientsInput.value);
  recipientCountEl.textContent = `${list.length} recipient${list.length !== 1 ? "s" : ""}`;
}

recipientsInput.addEventListener("input", updateRecipientCount);
recipientsInput.addEventListener("paste", () => setTimeout(updateRecipientCount, 0));

function setStatus(message, type = "") {
  statusEl.textContent = message;
  statusEl.className = "status " + type;
}

function showResults(results) {
  resultsCard.hidden = false;
  resultsList.innerHTML = "";
  for (const r of results) {
    const li = document.createElement("li");
    const badge = document.createElement("span");
    badge.className = "badge " + (r.success ? "badge--ok" : "badge--fail");
    badge.textContent = r.success ? "OK" : "Failed";
    li.appendChild(badge);
    li.appendChild(document.createTextNode(r.to + (r.error ? " — " + r.error : "")));
    resultsList.appendChild(li);
  }
}

sendAllBtn.addEventListener("click", async () => {
  const gmail = gmailInput.value.trim();
  const appPassword = appPasswordInput.value.trim();
  const subject = subjectInput.value.trim();
  const body = bodyInput.value.trim();
  const recipients = parseRecipients(recipientsInput.value);

  if (!gmail || !appPassword) {
    setStatus("Please enter your Gmail and App Password.", "error");
    return;
  }
  if (!subject) {
    setStatus("Please enter a subject.", "error");
    return;
  }
  if (!recipients.length) {
    setStatus("Please add at least one recipient (one email per line).", "error");
    return;
  }

  sendAllBtn.disabled = true;
  setStatus("Sending…");

  const emails = recipients.map((to) => ({ to, subject, body: body || "(No body)" }));

  try {
    const res = await fetch(`${API_BASE}/api/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gmail,
        appPassword,
        emails,
      }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      setStatus(data.error || `Error ${res.status}`, "error");
      sendAllBtn.disabled = false;
      return;
    }

    const results = data.results || [];
    const ok = results.filter((r) => r.success).length;
    const fail = results.filter((r) => !r.success).length;
    setStatus(`Done: ${ok} sent, ${fail} failed.`, fail ? "" : "success");
    showResults(results);
  } catch (err) {
    setStatus("Network error: " + (err.message || "Could not reach server."), "error");
  } finally {
    sendAllBtn.disabled = false;
  }
});

updateRecipientCount();
