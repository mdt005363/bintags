"use strict";

const $ = (id) => document.getElementById(id);
let lastItem = null;
let codeReader = null;

// ---- tabs -----------------------------------------------------------------
document.querySelectorAll(".tab").forEach((t) => {
  t.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    $(t.dataset.tab).classList.add("active");
  });
});

// ---- single scan / lookup -------------------------------------------------
$("token").addEventListener("keydown", (e) => {
  if (e.key === "Enter") lookup($("token").value.trim());
});

async function lookup(token) {
  if (!token) return;
  $("scanMsg").textContent = "Looking up…";
  $("result").hidden = true;
  try {
    const r = await fetch("/api/resolve?token=" + encodeURIComponent(token));
    const data = await r.json();
    if (!data.ok || !data.found) {
      $("scanMsg").innerHTML = '<span class="notfound">Not found: ' + token + "</span>";
      return;
    }
    lastItem = data.item;
    renderResult(data.item);
    $("scanMsg").textContent = "";
  } catch (err) {
    $("scanMsg").textContent = "Error: " + err.message;
  }
}

function priceStr(p) {
  return p == null ? "—" : "$" + Number(p).toFixed(2);
}

function renderResult(it) {
  const src = it.price_source === "live" ? "live" : "cached";
  const desc = [it.description, it.extended_desc].filter(Boolean).join(" ");
  $("result").innerHTML =
    '<div class="desc">' + (desc || "(no description)") + "</div>" +
    '<div class="codes">' + (it.part_number || it.item_code || "") +
      " &nbsp;·&nbsp; " + (it.item_code || "") + "</div>" +
    '<div class="price">' + priceStr(it.price) +
      '<span class="badge ' + src + '">' + src + "</span></div>" +
    '<div class="meta">UOM ' + (it.selling_uom || "?") +
      " &nbsp;·&nbsp; avail " + (it.available == null ? "?" : it.available) +
      " &nbsp;·&nbsp; scan " + (it.scanned_token || "") + "</div>" +
    '<div class="printrow"><input id="copies" type="number" min="1" value="1">' +
      '<button id="printBtn" type="button">Print tag</button></div>';
  $("result").hidden = false;
  $("printBtn").addEventListener("click", printThermal);
}

async function printThermal() {
  if (!lastItem) return;
  $("scanMsg").textContent = "Printing…";
  try {
    const r = await fetch("/api/print/thermal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: lastItem.scanned_token,
        copies: Number($("copies").value) || 1,
      }),
    });
    const data = await r.json();
    $("scanMsg").textContent = data.ok ? "Sent to printer." : "Print failed: " + data.error;
    if (data.ok) {
      $("token").value = "";
      $("token").focus();
    }
  } catch (err) {
    $("scanMsg").textContent = "Error: " + err.message;
  }
}

// ---- camera scan (ZXing) --------------------------------------------------
$("camBtn").addEventListener("click", async () => {
  if (!window.ZXing) { $("scanMsg").textContent = "Camera library unavailable; type instead."; return; }
  const video = $("cam");
  if (!video.hidden) { stopCamera(); return; }
  video.hidden = false;
  $("camBtn").textContent = "Stop";
  codeReader = new ZXing.BrowserMultiFormatReader();
  try {
    await codeReader.decodeFromVideoDevice(null, video, (res) => {
      if (res) { stopCamera(); $("token").value = res.getText(); lookup(res.getText()); }
    });
  } catch (e) {
    $("scanMsg").textContent = "Camera error: " + e.message;
    stopCamera();
  }
});

function stopCamera() {
  if (codeReader) { try { codeReader.reset(); } catch (e) {} codeReader = null; }
  $("cam").hidden = true;
  $("camBtn").textContent = "Camera";
}

// ---- batch sheet ----------------------------------------------------------
$("batchScan").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const v = $("batchScan").value.trim();
    if (v) { $("batchList").value += (($("batchList").value && "\n") || "") + v; $("batchScan").value = ""; }
  }
});

let batchRecords = [];

$("resolveBtn").addEventListener("click", async () => {
  const tokens = $("batchList").value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
  if (!tokens.length) return;
  $("batchMsg").textContent = "Resolving " + tokens.length + "…";
  const r = await fetch("/api/batch/resolve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tokens }),
  });
  const data = await r.json();
  batchRecords = data.rows.filter((x) => x.found).map((x) => x.item);
  renderBatch(data.rows);
  $("batchMsg").textContent = batchRecords.length + " resolved, " +
    data.rows.filter((x) => !x.found).length + " not found";
});

function renderBatch(rows) {
  let html = "<table><tr><th>Token</th><th>Item</th><th>Description</th><th>Price</th></tr>";
  rows.forEach((x) => {
    if (x.found) {
      const it = x.item;
      html += "<tr><td>" + x.token + "</td><td>" + (it.item_code || "") + "</td><td>" +
        (it.description || "") + "</td><td>" + priceStr(it.price) + "</td></tr>";
    } else {
      html += '<tr class="notfound"><td>' + x.token + "</td><td colspan=3>not found</td></tr>";
    }
  });
  html += "</table>";
  $("batchTable").innerHTML = html;
}

$("previewBtn").addEventListener("click", () => sheet(true));
$("printSheetBtn").addEventListener("click", () => sheet(false));

async function sheet(preview) {
  if (!batchRecords.length) { $("batchMsg").textContent = "Resolve some items first."; return; }
  const payload = { records: batchRecords, start_cell: Number($("startCell").value) || 1, preview };
  if (preview) {
    const r = await fetch("/api/print/sheet", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    const blob = await r.blob();
    window.open(URL.createObjectURL(blob), "_blank");
    return;
  }
  const r = await fetch("/api/print/sheet", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
  });
  const data = await r.json();
  $("batchMsg").textContent = data.ok ? "Sheet sent: " + data.status : "Failed: " + data.error;
}
