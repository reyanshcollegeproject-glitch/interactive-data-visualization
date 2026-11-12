/**
 * The Interactive Career Pivot & Financial Runway Decision Engine
 * Apple HIG-inspired Mathematical Simulation and Canvas Visualization
 */

// Application State
const state = {
  savings: 35000,
  burn: 3800,
  targetRevenue: 5500,
  rampMonths: 6,
  taxBuffer: true,
  sideGig: false,
  activePreset: 'startup',
  hoveredMonthIndex: null
};

// Preset Scenarios
const PRESETS = {
  startup: {
    name: 'Tech Venture Leap',
    savings: 38000,
    burn: 3800,
    targetRevenue: 6000,
    rampMonths: 7,
    taxBuffer: true,
    sideGig: false
  },
  freelance: {
    name: 'Campus to Studio',
    savings: 14000,
    burn: 2200,
    targetRevenue: 3800,
    rampMonths: 4,
    taxBuffer: false,
    sideGig: true
  },
  sabbatical: {
    name: 'Higher Ed Pivot',
    savings: 42000,
    burn: 2600,
    targetRevenue: 0,
    rampMonths: 12,
    taxBuffer: false,
    sideGig: false
  },
  conservative: {
    name: 'Cautious Safety',
    savings: 60000,
    burn: 3200,
    targetRevenue: 4500,
    rampMonths: 9,
    taxBuffer: true,
    sideGig: false
  }
};

// Format Currency
function formatUSD(val) {
  const rounded = Math.round(val);
  const prefix = rounded < 0 ? '-$' : '$';
  return prefix + Math.abs(rounded).toLocaleString('en-US');
}

// Compute Model Math
function computeSimulation(s = state) {
  const months = 24;
  const history = [];
  
  const taxMultiplier = s.taxBuffer ? 1.18 : 1.0;
  const effectiveMonthlyBurn = s.burn * taxMultiplier;
  const sideIncome = s.sideGig ? 1200 : 0;
  
  let currentCash = s.savings;
  let runwayMonths = null;
  let breakEvenMonth = null;
  let minBalance = currentCash;
  let minBalanceMonth = 0;
  
  // Month 0 (Starting point)
  history.push({
    month: 0,
    cash: currentCash,
    revenue: 0,
    burn: effectiveMonthlyBurn,
    netFlow: -effectiveMonthlyBurn
  });
  
  for (let m = 1; m <= months; m++) {
    // Primary revenue ramp-up (linear progression until rampMonths, then stable)
    let primaryRev = 0;
    if (m <= s.rampMonths) {
      primaryRev = s.targetRevenue * (m / s.rampMonths);
    } else {
      primaryRev = s.targetRevenue;
    }
    
    const totalRev = primaryRev + sideIncome;
    const netFlow = totalRev - effectiveMonthlyBurn;
    const prevCash = currentCash;
    currentCash += netFlow;
    
    // Check break-even month
    if (breakEvenMonth === null && totalRev >= effectiveMonthlyBurn) {
      breakEvenMonth = m;
    }
    
    // Check runway zero crossover
    if (runwayMonths === null && currentCash <= 0) {
      // Linear interpolation for exact fractional month
      const frac = prevCash / (prevCash - currentCash);
      runwayMonths = (m - 1) + frac;
    }
    
    if (currentCash < minBalance) {
      minBalance = currentCash;
      minBalanceMonth = m;
    }
    
    history.push({
      month: m,
      cash: currentCash,
      revenue: totalRev,
      burn: effectiveMonthlyBurn,
      netFlow: netFlow
    });
  }
  
  // Final runway determination
  const finalMonth = history[history.length - 1];
  let runwayDisplay = '';
  let statusTier = 'safe'; // 'safe', 'caution', 'risk'
  let statusMessage = '';
  
  if (runwayMonths !== null) {
    runwayDisplay = `${runwayMonths.toFixed(1)} mo`;
    if (runwayMonths < 8) {
      statusTier = 'risk';
      statusMessage = 'Critical: Capital depletion within 8 months. Reduce burn or accelerate revenue.';
    } else if (runwayMonths < 16) {
      statusTier = 'caution';
      statusMessage = 'Moderate Risk: Sustainable near-term, but requires tight budget discipline.';
    } else {
      statusTier = 'caution';
      statusMessage = 'Adequate: Sufficient buffer to reach target traction.';
    }
  } else {
    // Never depleted in 24 months
    if (finalMonth.netFlow >= 0) {
      runwayDisplay = 'Infinite (Self-Sustaining)';
      statusTier = 'safe';
      statusMessage = 'Ideal Scenario: Break-even attained before reserves hit zero.';
    } else {
      // Still positive cash at 24mo, but negative burn
      const extraMonths = finalMonth.cash / Math.abs(finalMonth.netFlow);
      const totalEstimated = (24 + extraMonths).toFixed(1);
      runwayDisplay = `${totalEstimated}+ mo`;
      statusTier = 'safe';
      statusMessage = 'Robust: Reserves extend well past the 24-month planning horizon.';
    }
  }
  
  const netDelta = finalMonth.cash - s.savings;
  
  // Sensitivity analysis: Impact of reducing burn by $300
  const reducedBurn = Math.max(1000, s.burn - 300);
  const testState = { ...s, burn: reducedBurn };
  const testSim = computeSimulationQuick(testState);
  let sensitivityBurnGain = '';
  if (runwayMonths !== null && testSim.runwayMonths !== null) {
    const diff = (testSim.runwayMonths - runwayMonths).toFixed(1);
    sensitivityBurnGain = `+${diff} months extended runway`;
  } else if (runwayMonths !== null && testSim.runwayMonths === null) {
    sensitivityBurnGain = 'Unlocks complete self-sustainability!';
  } else {
    sensitivityBurnGain = `+${formatUSD(300 * 24 * taxMultiplier)} preserved over 24mo`;
  }
  
  return {
    history,
    runwayMonths,
    runwayDisplay,
    breakEvenMonth,
    minBalance,
    minBalanceMonth,
    netDelta,
    effectiveMonthlyBurn,
    statusTier,
    statusMessage,
    sensitivityBurnGain
  };
}

// Lightweight simulation helper for what-if scenarios
function computeSimulationQuick(s) {
  const taxMultiplier = s.taxBuffer ? 1.18 : 1.0;
  const burn = s.burn * taxMultiplier;
  const side = s.sideGig ? 1200 : 0;
  let cash = s.savings;
  let runwayMonths = null;
  
  for (let m = 1; m <= 36; m++) {
    const primaryRev = m <= s.rampMonths ? s.targetRevenue * (m / s.rampMonths) : s.targetRevenue;
    const net = (primaryRev + side) - burn;
    const prev = cash;
    cash += net;
    if (runwayMonths === null && cash <= 0) {
      const frac = prev / (prev - cash);
      runwayMonths = (m - 1) + frac;
      break;
    }
  }
  return { runwayMonths, finalCash: cash };
}

// DOM Elements Cache
const DOM = {};

function initDOM() {
  DOM.savingsRange = document.getElementById('savingsRange');
  DOM.savingsVal = document.getElementById('savingsVal');
  DOM.burnRange = document.getElementById('burnRange');
  DOM.burnVal = document.getElementById('burnVal');
  DOM.revenueRange = document.getElementById('revenueRange');
  DOM.revenueVal = document.getElementById('revenueVal');
  DOM.rampRange = document.getElementById('rampRange');
  DOM.rampVal = document.getElementById('rampVal');
  DOM.taxBufferToggle = document.getElementById('taxBufferToggle');
  DOM.sideGigToggle = document.getElementById('sideGigToggle');
  
  DOM.kpiRunway = document.getElementById('kpiRunway');
  DOM.kpiRunwayPill = document.getElementById('kpiRunwayPill');
  DOM.kpiBreakEven = document.getElementById('kpiBreakEven');
  DOM.kpiMinCash = document.getElementById('kpiMinCash');
  DOM.kpiMinCashSub = document.getElementById('kpiMinCashSub');
  DOM.kpiNetDelta = document.getElementById('kpiNetDelta');
  DOM.kpiNetDeltaPill = document.getElementById('kpiNetDeltaPill');
  
  DOM.insightStatusTitle = document.getElementById('insightStatusTitle');
  DOM.insightStatusText = document.getElementById('insightStatusText');
  DOM.insightSensitivityText = document.getElementById('insightSensitivityText');
  DOM.insightTargetRevText = document.getElementById('insightTargetRevText');
  
  DOM.canvas = document.getElementById('runwayCanvas');
  DOM.tooltip = document.getElementById('chartTooltip');
  DOM.canvasContainer = document.querySelector('.canvas-container');
  
  DOM.presetTabs = document.querySelectorAll('.segmented-tab');
  DOM.btnReset = document.getElementById('btnReset');
  DOM.btnExport = document.getElementById('btnExport');
}

// Update UI Sliders Track Background Fill (Apple style)
function updateSliderProgress(slider) {
  const min = parseFloat(slider.min) || 0;
  const max = parseFloat(slider.max) || 100;
  const val = parseFloat(slider.value) || 0;
  const percentage = ((val - min) / (max - min)) * 100;
  slider.style.background = `linear-gradient(to right, #0071E3 0%, #0071E3 ${percentage}%, #E5E5EA ${percentage}%, #E5E5EA 100%)`;
}

// Refresh all input readouts
function updateReadouts() {
  DOM.savingsVal.textContent = formatUSD(state.savings);
  DOM.burnVal.textContent = `${formatUSD(state.burn)}/mo`;
  DOM.revenueVal.textContent = `${formatUSD(state.targetRevenue)}/mo`;
  DOM.rampVal.textContent = `${state.rampMonths} mo`;
  
  updateSliderProgress(DOM.savingsRange);
  updateSliderProgress(DOM.burnRange);
  updateSliderProgress(DOM.revenueRange);
  updateSliderProgress(DOM.rampRange);
}

// Apply Preset
function applyPreset(presetKey) {
  const p = PRESETS[presetKey];
  if (!p) return;
  state.activePreset = presetKey;
  state.savings = p.savings;
  state.burn = p.burn;
  state.targetRevenue = p.targetRevenue;
  state.rampMonths = p.rampMonths;
  state.taxBuffer = p.taxBuffer;
  state.sideGig = p.sideGig;
  
  DOM.savingsRange.value = state.savings;
  DOM.burnRange.value = state.burn;
  DOM.revenueRange.value = state.targetRevenue;
  DOM.rampRange.value = state.rampMonths;
  DOM.taxBufferToggle.checked = state.taxBuffer;
  DOM.sideGigToggle.checked = state.sideGig;
  
  DOM.presetTabs.forEach(tab => {
    tab.classList.toggle('active', tab.dataset.preset === presetKey);
  });
  
  render();
}

// Render UI & Charts
function render() {
  updateReadouts();
  const sim = computeSimulation(state);
  
  // 1. KPI Cards
  DOM.kpiRunway.textContent = sim.runwayDisplay;
  
  // Status Pills
  if (sim.statusTier === 'safe') {
    DOM.kpiRunwayPill.className = 'kpi-pill pill-green';
    DOM.kpiRunwayPill.textContent = 'High Viability';
  } else if (sim.statusTier === 'caution') {
    DOM.kpiRunwayPill.className = 'kpi-pill pill-orange';
    DOM.kpiRunwayPill.textContent = 'Caution Zone';
  } else {
    DOM.kpiRunwayPill.className = 'kpi-pill pill-red';
    DOM.kpiRunwayPill.textContent = 'Cliff Risk';
  }
  
  DOM.kpiBreakEven.textContent = sim.breakEvenMonth ? `Month ${sim.breakEvenMonth}` : 'Not in 24mo';
  
  if (sim.minBalance < 0) {
    DOM.kpiMinCash.textContent = '$0 (Depleted)';
    DOM.kpiMinCashSub.textContent = `Deficit reaches ${formatUSD(sim.minBalance)} by M24`;
  } else {
    DOM.kpiMinCash.textContent = formatUSD(sim.minBalance);
    DOM.kpiMinCashSub.textContent = sim.minBalanceMonth === 0 
      ? 'Initial reserve is the baseline' 
      : `Trough reaches in Month ${sim.minBalanceMonth}`;
  }
  
  DOM.kpiNetDelta.textContent = (sim.netDelta >= 0 ? '+' : '') + formatUSD(sim.netDelta);
  if (sim.netDelta >= 0) {
    DOM.kpiNetDeltaPill.className = 'kpi-pill pill-green';
    DOM.kpiNetDeltaPill.textContent = 'Net Positive';
  } else {
    DOM.kpiNetDeltaPill.className = 'kpi-pill pill-red';
    DOM.kpiNetDeltaPill.textContent = 'Net Capital Drain';
  }
  
  // 2. Strategic Insights
  DOM.insightStatusTitle.textContent = sim.statusTier === 'safe' ? 'Favorable Runway Horizon' : (sim.statusTier === 'caution' ? 'Buffer Warning' : 'Critical Cash Runway Alert');
  DOM.insightStatusText.textContent = sim.statusMessage;
  DOM.insightSensitivityText.textContent = `Reducing monthly expenses by $300 grants ${sim.sensitivityBurnGain}.`;
  
  const breakevenRequired = Math.round(sim.effectiveMonthlyBurn - (state.sideGig ? 1200 : 0));
  DOM.insightTargetRevText.textContent = `Target monthly revenue needed for immediate self-sufficiency is ${formatUSD(breakevenRequired)}/mo.`;
  
  // 3. Render Canvas Chart
  drawChart(sim);
  
  // 4. Update Sanity Check Values in UI
  const sanitySumCheck = document.getElementById('sanitySumCheck');
  if (sanitySumCheck) {
    const totalRevAll = sim.history.slice(1).reduce((acc, h) => acc + h.revenue, 0);
    const totalBurnAll = sim.history.slice(1).reduce((acc, h) => acc + h.burn, 0);
    const calculatedEnding = state.savings + totalRevAll - totalBurnAll;
    const finalHistCash = sim.history[sim.history.length - 1].cash;
    const diff = Math.abs(calculatedEnding - finalHistCash);
    sanitySumCheck.textContent = `Verified: $${state.savings.toLocaleString()} (Start) + $${Math.round(totalRevAll).toLocaleString()} (Rev) - $${Math.round(totalBurnAll).toLocaleString()} (Burn) = $${Math.round(finalHistCash).toLocaleString()} (Δ = ${diff.toFixed(2)})`;
  }
}

// Chart Rendering on Retina Canvas
function drawChart(sim) {
  const canvas = DOM.canvas;
  const ctx = canvas.getContext('2d');
  
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  
  // Set real pixel dimensions for sharp retina display
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  
  ctx.save();
  ctx.scale(dpr, dpr);
  
  const w = rect.width;
  const h = rect.height;
  
  ctx.clearRect(0, 0, w, h);
  
  const padding = { top: 25, right: 30, bottom: 40, left: 65 };
  const plotW = w - padding.left - padding.right;
  const plotH = h - padding.top - padding.bottom;
  
  const history = sim.history;
  const cashValues = history.map(h => h.cash);
  
  // Determine dynamic Y-axis bounds
  let maxCash = Math.max(...cashValues, state.savings, 10000);
  let minCash = Math.min(...cashValues, 0);
  
  // Pad bounds gracefully
  const ySpan = maxCash - minCash;
  maxCash += ySpan * 0.12;
  minCash -= ySpan * 0.08;
  
  const getX = (m) => padding.left + (m / 24) * plotW;
  const getY = (c) => padding.top + plotH - ((c - minCash) / (maxCash - minCash)) * plotH;
  
  // Draw Subtle Horizontal Grid Lines
  ctx.lineWidth = 1;
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.05)';
  ctx.fillStyle = '#86868B';
  ctx.font = '11px -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif';
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';
  
  const gridSteps = 5;
  for (let i = 0; i <= gridSteps; i++) {
    const val = minCash + (i / gridSteps) * (maxCash - minCash);
    const yPos = getY(val);
    
    ctx.beginPath();
    ctx.moveTo(padding.left, yPos);
    ctx.lineTo(padding.left + plotW, yPos);
    ctx.stroke();
    
    ctx.fillText(formatUSD(val), padding.left - 10, yPos);
  }
  
  // Zero Threshold Line (Red/Grey Dashed)
  if (minCash < 0 && maxCash > 0) {
    const zeroY = getY(0);
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 59, 48, 0.55)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padding.left, zeroY);
    ctx.lineTo(padding.left + plotW, zeroY);
    ctx.stroke();
    
    ctx.fillStyle = '#FF3B30';
    ctx.textAlign = 'left';
    ctx.fillText('$0 Depletion Line', padding.left + plotW - 100, zeroY - 8);
    ctx.restore();
  }
  
  // Draw Month Ticks (X Axis)
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  ctx.fillStyle = '#86868B';
  for (let m = 0; m <= 24; m += 3) {
    const xPos = getX(m);
    ctx.fillText(`M${m}`, xPos, padding.top + plotH + 10);
  }
  
  // Monthly Revenue Ramp Subtle Line (Green)
  ctx.beginPath();
  for (let m = 0; m <= 24; m++) {
    const rev = history[m].revenue;
    // Scale revenue to fit in lower visual band
    const xPos = getX(m);
    const yPos = getY(rev);
    if (m === 0) ctx.moveTo(xPos, yPos);
    else ctx.lineTo(xPos, yPos);
  }
  ctx.strokeStyle = 'rgba(52, 199, 89, 0.45)';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([3, 3]);
  ctx.stroke();
  ctx.setLineDash([]);
  
  // Monthly Burn Subtle Line (Red)
  ctx.beginPath();
  for (let m = 0; m <= 24; m++) {
    const burn = history[m].burn;
    const xPos = getX(m);
    const yPos = getY(burn);
    if (m === 0) ctx.moveTo(xPos, yPos);
    else ctx.lineTo(xPos, yPos);
  }
  ctx.strokeStyle = 'rgba(255, 59, 48, 0.35)';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([3, 3]);
  ctx.stroke();
  ctx.setLineDash([]);
  
  // Draw Cash Balance Gradient Area
  const zeroBaselineY = Math.min(padding.top + plotH, Math.max(padding.top, getY(Math.max(0, minCash))));
  const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + plotH);
  gradient.addColorStop(0, 'rgba(0, 113, 227, 0.18)');
  gradient.addColorStop(0.8, 'rgba(0, 113, 227, 0.03)');
  gradient.addColorStop(1, 'rgba(0, 113, 227, 0.0)');
  
  ctx.beginPath();
  ctx.moveTo(getX(0), zeroBaselineY);
  ctx.lineTo(getX(0), getY(history[0].cash));
  
  for (let m = 1; m <= 24; m++) {
    const prevX = getX(m - 1);
    const prevY = getY(history[m - 1].cash);
    const currX = getX(m);
    const currY = getY(history[m].cash);
    const midX = (prevX + currX) / 2;
    ctx.bezierCurveTo(midX, prevY, midX, currY, currX, currY);
  }
  
  ctx.lineTo(getX(24), zeroBaselineY);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();
  
  // Draw Cash Balance Curve (Smooth Apple Blue Line)
  ctx.beginPath();
  ctx.moveTo(getX(0), getY(history[0].cash));
  
  for (let m = 1; m <= 24; m++) {
    const prevX = getX(m - 1);
    const prevY = getY(history[m - 1].cash);
    const currX = getX(m);
    const currY = getY(history[m].cash);
    const midX = (prevX + currX) / 2;
    ctx.bezierCurveTo(midX, prevY, midX, currY, currX, currY);
  }
  
  ctx.strokeStyle = '#0071E3';
  ctx.lineWidth = 2.8;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();
  
  // Draw Data Points
  for (let m = 0; m <= 24; m += 2) {
    const xPos = getX(m);
    const yPos = getY(history[m].cash);
    
    ctx.beginPath();
    ctx.arc(xPos, yPos, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#FFFFFF';
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#0071E3';
    ctx.stroke();
  }
  
  // Highlight Break-Even Marker if reached
  if (sim.breakEvenMonth && sim.breakEvenMonth <= 24) {
    const beX = getX(sim.breakEvenMonth);
    const beY = getY(history[sim.breakEvenMonth].cash);
    
    ctx.save();
    ctx.beginPath();
    ctx.arc(beX, beY, 6.5, 0, Math.PI * 2);
    ctx.fillStyle = '#34C759';
    ctx.fill();
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    ctx.fillStyle = '#1D1D1F';
    ctx.font = '600 11px -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif';
    ctx.fillText(`Break-Even (M${sim.breakEvenMonth})`, beX, beY - 14);
    ctx.restore();
  }
  
  // Highlight Hovered Month
  if (state.hoveredMonthIndex !== null && state.hoveredMonthIndex >= 0 && state.hoveredMonthIndex <= 24) {
    const m = state.hoveredMonthIndex;
    const xPos = getX(m);
    const yPos = getY(history[m].cash);
    
    // Vertical Crosshair
    ctx.save();
    ctx.strokeStyle = 'rgba(0, 113, 227, 0.35)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(xPos, padding.top);
    ctx.lineTo(xPos, padding.top + plotH);
    ctx.stroke();
    
    // Glowing active point
    ctx.beginPath();
    ctx.arc(xPos, yPos, 7, 0, Math.PI * 2);
    ctx.fillStyle = '#0071E3';
    ctx.fill();
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();
  }
  
  ctx.restore();
}

// Mouse / Touch Interaction for Interactive Canvas Hover
function handleCanvasPointer(e) {
  const canvas = DOM.canvas;
  const rect = canvas.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  
  const x = clientX - rect.left;
  const y = clientY - rect.top;
  
  const padding = { top: 25, right: 30, bottom: 40, left: 65 };
  const plotW = rect.width - padding.left - padding.right;
  
  if (x < padding.left || x > rect.width - padding.right) {
    DOM.tooltip.style.display = 'none';
    state.hoveredMonthIndex = null;
    drawChart(computeSimulation(state));
    return;
  }
  
  const normalized = (x - padding.left) / plotW;
  const month = Math.min(24, Math.max(0, Math.round(normalized * 24)));
  state.hoveredMonthIndex = month;
  
  const sim = computeSimulation(state);
  const data = sim.history[month];
  
  // Populate Tooltip
  DOM.tooltip.innerHTML = `
    <div class="tooltip-month">Month ${month} ${month === 0 ? '(Launch)' : ''}</div>
    <div class="tooltip-row">
      <span style="color:#A1A1A6">Reserve Balance</span>
      <span class="tooltip-val" style="color:${data.cash >= 0 ? '#FFFFFF' : '#FF453A'}">${formatUSD(data.cash)}</span>
    </div>
    <div class="tooltip-row">
      <span style="color:#A1A1A6">Monthly Revenue</span>
      <span class="tooltip-val" style="color:#32D74B">${formatUSD(data.revenue)}</span>
    </div>
    <div class="tooltip-row">
      <span style="color:#A1A1A6">Monthly Burn</span>
      <span class="tooltip-val" style="color:#FF6961">${formatUSD(data.burn)}</span>
    </div>
    <div class="tooltip-row" style="border-top: 1px solid rgba(255,255,255,0.15); margin-top: 4px; padding-top: 4px;">
      <span style="color:#A1A1A6">Net Flow</span>
      <span class="tooltip-val" style="color:${data.netFlow >= 0 ? '#32D74B' : '#FF453A'}">${(data.netFlow >= 0 ? '+' : '') + formatUSD(data.netFlow)}/mo</span>
    </div>
  `;
  
  DOM.tooltip.style.display = 'block';
  DOM.tooltip.style.left = `${clientX - rect.left}px`;
  DOM.tooltip.style.top = `${Math.max(10, clientY - rect.top - 15)}px`;
  
  drawChart(sim);
}

function handlePointerLeave() {
  DOM.tooltip.style.display = 'none';
  state.hoveredMonthIndex = null;
  drawChart(computeSimulation(state));
}

// Attach Event Listeners
function attachEvents() {
  // Sliders
  DOM.savingsRange.addEventListener('input', (e) => {
    state.savings = parseFloat(e.target.value);
    render();
  });
  
  DOM.burnRange.addEventListener('input', (e) => {
    state.burn = parseFloat(e.target.value);
    render();
  });
  
  DOM.revenueRange.addEventListener('input', (e) => {
    state.targetRevenue = parseFloat(e.target.value);
    render();
  });
  
  DOM.rampRange.addEventListener('input', (e) => {
    state.rampMonths = parseInt(e.target.value, 10);
    render();
  });
  
  // Toggles
  DOM.taxBufferToggle.addEventListener('change', (e) => {
    state.taxBuffer = e.target.checked;
    render();
  });
  
  DOM.sideGigToggle.addEventListener('change', (e) => {
    state.sideGig = e.target.checked;
    render();
  });
  
  // Presets
  DOM.presetTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      applyPreset(tab.dataset.preset);
    });
  });
  
  // Canvas interactions
  DOM.canvas.addEventListener('mousemove', handleCanvasPointer);
  DOM.canvas.addEventListener('mouseleave', handlePointerLeave);
  DOM.canvas.addEventListener('touchmove', handleCanvasPointer, { passive: true });
  DOM.canvas.addEventListener('touchend', handlePointerLeave);
  
  // Resize handler
  window.addEventListener('resize', () => {
    drawChart(computeSimulation(state));
  });
  
  // Action Buttons
  if (DOM.btnReset) {
    DOM.btnReset.addEventListener('click', () => {
      applyPreset('startup');
    });
  }
  
  if (DOM.btnExport) {
    DOM.btnExport.addEventListener('click', () => {
      window.print();
    });
  }
}

// Initialization on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initDOM();
  attachEvents();
  applyPreset('startup');
});
