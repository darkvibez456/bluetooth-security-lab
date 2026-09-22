const scenarioSelect = document.querySelector('#scenario');
const intensity = document.querySelector('#intensity');
const intensityValue = document.querySelector('#intensityValue');
const scenarioCard = document.querySelector('#scenarioCard');
const result = document.querySelector('#result');
let scenarios = [];

function updateIntensity() {
  intensityValue.value = intensity.value;
  intensityValue.textContent = intensity.value;
}

function updateScenarioCard() {
  const item = scenarios.find(entry => entry.id === scenarioSelect.value);
  if (!item) return;
  scenarioCard.innerHTML = `<div class="section-label">Scenario brief</div><h2>${item.title}</h2><p>${item.description}</p><div class="lesson-chip">Defensive focus <span>${item.lesson}</span></div>`;
}

intensity.addEventListener('input', updateIntensity);
scenarioSelect.addEventListener('change', updateScenarioCard);

document.querySelector('#run').addEventListener('click', async () => {
  result.className = 'panel result loading';
  result.innerHTML = '<div class="spinner"></div><p>Generating a reproducible synthetic trace…</p>';
  try {
    const response = await fetch('/api/simulate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({scenario: scenarioSelect.value, intensity: Number(intensity.value), seed: 7})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Simulation failed');
    result.className = 'panel result';
    result.innerHTML = `<div class="result-head"><div><div class="section-label">02 / Read the signal</div><h2>${data.scenario_title}</h2><p>${data.lesson}</p></div><div class="score"><span>${data.risk_score}</span><small>/100<br>training score</small></div></div>
      <div class="metric-row"><div><b>${data.events.length}</b><span>synthetic events</span></div><div><b>SIM-####</b><span>identifier format</span></div><div><b>OFF</b><span>hardware access</span></div></div>
      <div class="result-grid"><div><h3>Recommended controls</h3><ul>${data.recommended_controls.map(x => `<li>${x}</li>`).join('')}</ul></div><div><h3>Event stream <span class="muted">latest synthetic observations</span></h3><div class="events">${data.events.map(e => `<div class="event"><code>${e.synthetic_device}</code><span>${e.event_type.replaceAll('_', ' ')}</span><b class="${e.severity}">${e.severity}</b></div>`).join('')}</div></div></div>`;
  } catch (error) {
    result.className = 'panel result error';
    result.textContent = error.message;
  }
});

async function loadScenarios() {
  const data = await fetch('/api/scenarios').then(r => r.json());
  scenarios = data.scenarios;
  scenarioSelect.innerHTML = scenarios.map(item => `<option value="${item.id}">${item.title}</option>`).join('');
  updateScenarioCard();
}

loadScenarios().catch(() => { scenarioCard.innerHTML = '<div class="section-label">Backend unavailable</div><h2>Start the local server first</h2><p>Run <code>python3 backend/server.py</code> in the project directory.</p>'; });
updateIntensity();
