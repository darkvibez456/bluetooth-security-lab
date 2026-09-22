const scenarioSelect = document.querySelector('#scenario');
const intensity = document.querySelector('#intensity');
const intensityValue = document.querySelector('#intensityValue');
const scenarioCard = document.querySelector('.scenario-card');
const hardwareStatus = document.querySelector('#hardwareStatus');
const authorized = document.querySelector('#authorized');
const scan = document.querySelector('#scan');
const result = document.querySelector('#result');
let scenarios = [];

const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
function updateIntensity() { intensityValue.value = intensity.value; intensityValue.textContent = intensity.value; }
function updateScenarioCard() {
  const item = scenarios.find(entry => entry.id === scenarioSelect.value);
  if (!item) return;
  scenarioCard.querySelector('.section-label').textContent = '02 / Synthetic scenario';
  scenarioCard.querySelector('#hardwareStatus').innerHTML = `<h2>${escapeHtml(item.title)}</h2><p>${escapeHtml(item.description)}</p><div class="lesson-chip">Defensive focus <span>${escapeHtml(item.lesson)}</span></div>`;
}
function showError(message) { result.className = 'panel result error'; result.textContent = message; }
function renderSimulation(data) {
  result.className = 'panel result';
  result.innerHTML = `<div class="result-head"><div><div class="section-label">03 / Synthetic signal</div><h2>${escapeHtml(data.scenario_title)}</h2><p>${escapeHtml(data.lesson)}</p></div><div class="score"><span>${data.risk_score}</span><small>/100<br>training score</small></div></div><div class="metric-row"><div><b>${data.events.length}</b><span>synthetic events</span></div><div><b>SIM-####</b><span>identifier format</span></div><div><b>OFF</b><span>hardware access</span></div></div><div class="result-grid"><div><h3>Recommended controls</h3><ul>${data.recommended_controls.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul></div><div><h3>Event stream <span class="muted">synthetic observations</span></h3><div class="events">${data.events.map(e => `<div class="event"><code>${escapeHtml(e.synthetic_device)}</code><span>${escapeHtml(e.event_type.replaceAll('_', ' '))}</span><b class="${escapeHtml(e.severity)}">${escapeHtml(e.severity)}</b></div>`).join('')}</div></div></div>`;
}
function renderHardware(data) {
  result.className = 'panel result';
  const deviceRows = data.devices.length ? data.devices.map(device => `<div class="event hardware-event"><code>${escapeHtml(device.device_id)}</code><span>${escapeHtml(device.name)} <small>${device.observation_count} observations</small></span><b class="observed">seen</b></div>`).join('') : '<p class="muted">No advertisements observed in this window.</p>';
  result.innerHTML = `<div class="result-head"><div><div class="section-label">03 / Authorized hardware signal</div><h2>Read-only discovery complete</h2><p>Captured from the local adapter without revealing real addresses.</p></div><div class="score safe-score"><span>${data.device_count}</span><small>devices<br>observed</small></div></div><div class="metric-row"><div><b>${data.duration_seconds}s</b><span>scan window</span></div><div><b>MASKED</b><span>identifiers</span></div><div><b>OFF</b><span>pairing / packets</span></div></div><div class="result-grid"><div><h3>Privacy posture</h3><ul>${data.notes.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul></div><div><h3>Observed devices <span class="muted">ephemeral IDs only</span></h3><div class="events">${deviceRows}</div></div></div>`;
}
intensity.addEventListener('input', updateIntensity);
scenarioSelect.addEventListener('change', updateScenarioCard);
authorized.addEventListener('change', () => { scan.disabled = !authorized.checked; });
document.querySelector('#run').addEventListener('click', async () => {
  result.className = 'panel result loading'; result.innerHTML = '<div class="spinner"></div><p>Generating a reproducible synthetic trace…</p>';
  try { const response = await fetch('/api/simulate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({scenario:scenarioSelect.value,intensity:Number(intensity.value),seed:7})}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Simulation failed'); renderSimulation(data); } catch (error) { showError(error.message); }
});
scan.addEventListener('click', async () => {
  scan.disabled = true; result.className = 'panel result loading'; result.innerHTML = '<div class="spinner"></div><p>Listening for advertisements in the authorized window…</p>';
  try { const response = await fetch('/api/hardware/scan', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({confirm_authorized_scope:true,duration_seconds:Number(document.querySelector('#scanDuration').value)})}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Hardware discovery failed'); renderHardware(data); } catch (error) { showError(error.message); } finally { scan.disabled = !authorized.checked; }
});
async function loadScenarios() { const data = await fetch('/api/scenarios').then(r => r.json()); scenarios = data.scenarios; scenarioSelect.innerHTML = scenarios.map(item => `<option value="${item.id}">${escapeHtml(item.title)}</option>`).join(''); updateScenarioCard(); }
async function loadHardwareStatus() { const data = await fetch('/api/hardware/status').then(r => r.json()); hardwareStatus.innerHTML = data.available ? '<h2>Adapter available</h2><p>BlueZ read-only discovery is ready. Consent is required before each scan.</p>' : '<h2>Simulation only</h2><p>BlueZ / bluetoothctl was not detected. Install BlueZ and connect an adapter to enable hardware discovery.</p>'; }
loadScenarios().catch(() => { scenarioCard.querySelector('#hardwareStatus').innerHTML = '<h2>Backend unavailable</h2><p>Run <code>python3 backend/server.py</code> in the project directory.</p>'; });
loadHardwareStatus().catch(() => {}); updateIntensity();
