const scenario = document.querySelector('#scenario');
const intensity = document.querySelector('#intensity');
const intensityValue = document.querySelector('#intensityValue');
const result = document.querySelector('#result');

intensity.addEventListener('input', () => { intensityValue.value = intensity.value; intensityValue.textContent = intensity.value; });

async function loadScenarios() {
  const data = await fetch('/api/scenarios').then(r => r.json());
  for (const item of data.scenarios) {
    const option = document.createElement('option');
    option.value = item.id;
    option.textContent = item.title;
    option.title = item.description;
    scenario.appendChild(option);
  }
}

document.querySelector('#run').addEventListener('click', async () => {
  result.className = 'panel loading';
  result.textContent = 'Generating synthetic events…';
  const data = await fetch('/api/simulate', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({scenario: scenario.value, intensity: Number(intensity.value)})
  }).then(r => r.json());
  result.className = 'panel';
  result.innerHTML = `<div class="result-head"><div><p class="eyebrow">SIMULATION RESULT</p><h2>${data.scenario_title}</h2></div><div class="score">${data.risk_score}<small>/100</small></div></div>
    <p>${data.lesson}</p><h3>Recommended controls</h3><ul>${data.recommended_controls.map(x => `<li>${x}</li>`).join('')}</ul>
    <h3>Event stream <span class="muted">(${data.events.length} synthetic events)</span></h3>
    <div class="events">${data.events.map(e => `<div class="event"><code>${e.synthetic_device}</code><span>${e.event_type}</span><b class="${e.severity}">${e.severity}</b></div>`).join('')}</div>`;
});

loadScenarios().catch(() => { result.textContent = 'Backend unavailable. Start it with: python3 backend/server.py'; });
