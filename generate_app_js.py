import json

with open("real_data.json", "r") as f:
    real_data = json.load(f)

js_code = """/**
 * Runway Studio — Real Empirical Data Decision Engine
 * Data Provenance:
 * 1. U.S. Bureau of Labor Statistics (BLS) Occupational Employment & Wage Statistics (May 2024)
 * 2. U.S. Department of Housing & Urban Development (HUD) FY2024 Fair Market Rents (FMR)
 * 3. IRS & State Tax Foundation 2024 Progressive Brackets & FICA Limits
 * 4. MIT Living Wage Living Expense Benchmarks
 * 5. Robert Shiller S&P 500 & Consumer Price Index (CPI) Series (1970-2026)
 */

const REAL_DATA = """ + json.dumps(real_data, indent=2) + """;

// Application State
const state = {
  selectedMetro: 'san_francisco',
  annualGross: 178900,
  housingType: 'oneBed', // 'studio', 'oneBed', 'twoBed'
  initialSavings: 35000,
  discretionaryMonthly: 1200,
  isCareerPivot: false,
  selectedEra: 'recent_2020',
  hoveredMonthIndex: null
};

// Calculate Real IRS Federal, FICA, State, and Local Taxes
function calculateRealTax(gross, metro) {
  const standardDeduction = 14600;
  const taxable = Math.max(0, gross - standardDeduction);
  
  // IRS 2024 Brackets
  const brackets = [
    [11600, 0.10],
    [47150, 0.12],
    [100525, 0.22],
    [191950, 0.24],
    [243725, 0.32],
    [609350, 0.35],
    [Infinity, 0.37]
  ];
  
  let fedTax = 0;
  let prevLimit = 0;
  for (const [limit, rate] of brackets) {
    if (taxable > prevLimit) {
      const taxableInBracket = Math.min(taxable - prevLimit, limit - prevLimit);
      fedTax += taxableInBracket * rate;
      prevLimit = limit;
    } else {
      break;
    }
  }
  
  // FICA (Social Security 6.2% up to $168,600 + Medicare 1.45% uncapped + 0.9% additional over $200k)
  const ssTax = Math.min(gross, 168600) * 0.062;
  let medicareTax = gross * 0.0145;
  if (gross > 200000) {
    medicareTax += (gross - 200000) * 0.009;
  }
  const ficaTax = ssTax + medicareTax;
  
  // State and Local Taxes
  const stateTax = taxable * metro.stateIncomeTaxRate;
  const localTax = taxable * metro.localIncomeTaxRate;
  
  const totalTax = fedTax + ficaTax + stateTax + localTax;
  const netAnnual = Math.max(0, gross - totalTax);
  
  return {
    grossAnnual: gross,
    grossMonthly: gross / 12,
    federalTax: fedTax,
    ficaTax: ficaTax,
    stateTax: stateTax,
    localTax: localTax,
    totalTax: totalTax,
    effectiveTaxRate: (totalTax / gross) * 100,
    netAnnual: netAnnual,
    netMonthly: netAnnual / 12
  };
}

// Format Currency
function formatUSD(val) {
  const rounded = Math.round(val);
  const prefix = rounded < 0 ? '-$' : '$';
  return prefix + Math.abs(rounded).toLocaleString('en-US');
}

// Main Simulation Engine using Real Data
function computeRealSimulation() {
  const metro = REAL_DATA.metros[state.selectedMetro];
  const tax = calculateRealTax(state.annualGross, metro);
  const monthlyRent = metro.hudFmr[state.housingType];
  const monthlyEssentials = metro.mitLivingEssentials;
  const totalMonthlyBurn = monthlyRent + monthlyEssentials + state.discretionaryMonthly;
  
  const monthlyInflow = state.isCareerPivot ? 0 : tax.netMonthly;
  const netMonthlyCashFlow = monthlyInflow - totalMonthlyBurn;
  
  // Historical Market/Inflation Era parameters
  const eraData = REAL_DATA.marketHistoricalEras[state.selectedEra];
  const monthlySeries = eraData ? eraData.first36Months.slice(0, 24) : [];
  
  // 24-Month Discrete Cash Ledger
  const history = [];
  let currentCash = state.initialSavings;
  let runwayMonths = null;
  let minBalance = currentCash;
  let minBalanceMonth = 0;
  
  history.push({
    month: 0,
    cash: currentCash,
    inflow: monthlyInflow,
    burn: totalMonthlyBurn,
    netFlow: netMonthlyCashFlow,
    realCash: currentCash
  });
  
  let cumulativeInflation = 1.0;
  
  for (let m = 1; m <= 24; m++) {
    const prevCash = currentCash;
    currentCash += netMonthlyCashFlow;
    
    // Real inflation adjustment from historical data
    const monthEra = monthlySeries[m - 1];
    const infRate = monthEra ? monthEra.monthlyInflation : 0.0025;
    cumulativeInflation *= (1 + infRate);
    const realAdjustedCash = currentCash / cumulativeInflation;
    
    if (runwayMonths === null && currentCash <= 0) {
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
      realCash: realAdjustedCash,
      inflow: monthlyInflow,
      burn: totalMonthlyBurn,
      netFlow: netMonthlyCashFlow
    });
  }
  
  const finalMonth = history[history.length - 1];
  const net24Delta = finalMonth.cash - state.initialSavings;
  const monthsToSave50k = netMonthlyCashFlow > 0 ? (50000 / netMonthlyCashFlow) : null;
  
  return {
    metro,
    tax,
    monthlyRent,
    monthlyEssentials,
    totalMonthlyBurn,
    netMonthlyCashFlow,
    runwayMonths,
    minBalance,
    minBalanceMonth,
    net24Delta,
    monthsToSave50k,
    history,
    eraData
  };
}

// DOM Cache
const DOM = {};

function initDOM() {
  DOM.metroSelect = document.getElementById('metroSelect');
  DOM.wageRange = document.getElementById('wageRange');
  DOM.wageVal = document.getElementById('wageVal');
  DOM.housingRadios = document.querySelectorAll('input[name="housingType"]');
  DOM.savingsRange = document.getElementById('savingsRange');
  DOM.savingsVal = document.getElementById('savingsVal');
  DOM.discretionaryRange = document.getElementById('discretionaryRange');
  DOM.discretionaryVal = document.getElementById('discretionaryVal');
  DOM.pivotToggle = document.getElementById('pivotToggle');
  DOM.eraSelect = document.getElementById('eraSelect');
  
  DOM.kpiNetMonthly = document.getElementById('kpiNetMonthly');
  DOM.kpiNetMonthlyPill = document.getElementById('kpiNetMonthlyPill');
  DOM.kpiTotalBurn = document.getElementById('kpiTotalBurn');
  DOM.kpiTotalBurnSub = document.getElementById('kpiTotalBurnSub');
  DOM.kpiSurplusOrRunway = document.getElementById('kpiSurplusOrRunway');
  DOM.kpiSurplusOrRunwayPill = document.getElementById('kpiSurplusOrRunwayPill');
  DOM.kpiSpeedTo50k = document.getElementById('kpiSpeedTo50k');
  DOM.kpiSpeedTo50kSub = document.getElementById('kpiSpeedTo50kSub');
  
  DOM.canvas = document.getElementById('runwayCanvas');
  DOM.tooltip = document.getElementById('chartTooltip');
  DOM.btnReset = document.getElementById('btnReset');
  DOM.btnExport = document.getElementById('btnExport');
  DOM.metroPills = document.querySelectorAll('.metro-pill');
}

function updateSliderProgress(slider) {
  const min = parseFloat(slider.min) || 0;
  const max = parseFloat(slider.max) || 100;
  const val = parseFloat(slider.value) || 0;
  const pct = ((val - min) / (max - min)) * 100;
  slider.style.background = `linear-gradient(to right, #0071E3 0%, #0071E3 ${pct}%, #E5E5EA ${pct}%, #E5E5EA 100%)`;
}

function render() {
  DOM.wageVal.textContent = formatUSD(state.annualGross) + '/yr';
  DOM.savingsVal.textContent = formatUSD(state.initialSavings);
  DOM.discretionaryVal.textContent = formatUSD(state.discretionaryMonthly) + '/mo';
  
  updateSliderProgress(DOM.wageRange);
  updateSliderProgress(DOM.savingsRange);
  updateSliderProgress(DOM.discretionaryRange);
  
  const sim = computeRealSimulation();
  
  // 1. KPI 1: Real Net Monthly Take-Home (IRS Taxes deducted)
  DOM.kpiNetMonthly.textContent = formatUSD(sim.tax.netMonthly) + '/mo';
  DOM.kpiNetMonthlyPill.textContent = `${sim.tax.effectiveTaxRate.toFixed(1)}% Eff. Tax`;
  DOM.kpiNetMonthlyPill.className = 'kpi-pill pill-blue';
  
  // 2. KPI 2: Total Real Living Burn
  DOM.kpiTotalBurn.textContent = formatUSD(sim.totalMonthlyBurn) + '/mo';
  DOM.kpiTotalBurnSub.textContent = `HUD Rent: ${formatUSD(sim.monthlyRent)} | Essentials: ${formatUSD(sim.monthlyEssentials)}`;
  
  // 3. KPI 3: Surplus or Runway Duration
  if (state.isCareerPivot) {
    if (sim.runwayMonths !== null) {
      DOM.kpiSurplusOrRunway.textContent = `${sim.runwayMonths.toFixed(1)} Months`;
      DOM.kpiSurplusOrRunwayPill.className = sim.runwayMonths < 8 ? 'kpi-pill pill-red' : 'kpi-pill pill-orange';
      DOM.kpiSurplusOrRunwayPill.textContent = 'Pivot Runway';
    } else {
      DOM.kpiSurplusOrRunway.textContent = '24+ Months';
      DOM.kpiSurplusOrRunwayPill.className = 'kpi-pill pill-green';
      DOM.kpiSurplusOrRunwayPill.textContent = 'Well Funded';
    }
  } else {
    DOM.kpiSurplusOrRunway.textContent = (sim.netMonthlyCashFlow >= 0 ? '+' : '') + formatUSD(sim.netMonthlyCashFlow) + '/mo';
    if (sim.netMonthlyCashFlow >= 0) {
      DOM.kpiSurplusOrRunwayPill.className = 'kpi-pill pill-green';
      DOM.kpiSurplusOrRunwayPill.textContent = 'Net Cash Surplus';
    } else {
      DOM.kpiSurplusOrRunwayPill.className = 'kpi-pill pill-red';
      DOM.kpiSurplusOrRunwayPill.textContent = 'Monthly Deficit';
    }
  }
  
  // 4. KPI 4: Speed to $50,000 Reserve
  if (sim.monthsToSave50k !== null && !state.isCareerPivot) {
    DOM.kpiSpeedTo50k.textContent = `${sim.monthsToSave50k.toFixed(1)} mo`;
    DOM.kpiSpeedTo50kSub.textContent = `Time to accumulate $50k reserve`;
  } else if (state.isCareerPivot) {
    DOM.kpiSpeedTo50k.textContent = sim.minBalance < 0 ? '$0 (Depleted)' : formatUSD(sim.minBalance);
    DOM.kpiSpeedTo50kSub.textContent = `Lowest reserve trough`;
  } else {
    DOM.kpiSpeedTo50k.textContent = 'Insolvent';
    DOM.kpiSpeedTo50kSub.textContent = 'Burn exceeds net take-home';
  }
  
  // Draw Retina Canvas Chart
  drawRealChart(sim);
  
  // Math Integrity Sanity Check
  const sanityEl = document.getElementById('sanitySumCheck');
  if (sanityEl) {
    sanityEl.textContent = `Real Data Provenance: ${sim.metro.name} | Gross: ${formatUSD(state.annualGross)} - Fed Tax: ${formatUSD(sim.tax.federalTax)} - FICA: ${formatUSD(sim.tax.ficaTax)} - State Tax: ${formatUSD(sim.tax.stateTax + sim.tax.localTax)} = Net: ${formatUSD(sim.tax.netAnnual)}/yr (${formatUSD(sim.tax.netMonthly)}/mo)`;
  }
}

// Draw High-DPI Canvas Chart
function drawRealChart(sim) {
  const canvas = DOM.canvas;
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  
  ctx.save();
  ctx.scale(dpr, dpr);
  
  const w = rect.width;
  const h = rect.height;
  ctx.clearRect(0, 0, w, h);
  
  const padding = { top: 25, right: 30, bottom: 40, left: 70 };
  const plotW = w - padding.left - padding.right;
  const plotH = h - padding.top - padding.bottom;
  
  const history = sim.history;
  const values = history.map(d => d.cash);
  let maxVal = Math.max(...values, state.initialSavings, 10000);
  let minVal = Math.min(...values, 0);
  
  const span = maxVal - minVal;
  maxVal += span * 0.12;
  minVal -= span * 0.08;
  
  const getX = (m) => padding.left + (m / 24) * plotW;
  const getY = (val) => padding.top + plotH - ((val - minVal) / (maxVal - minVal)) * plotH;
  
  // Grid Lines
  ctx.lineWidth = 1;
  ctx.strokeStyle = '#E5E5EA';
  ctx.fillStyle = '#86868B';
  ctx.font = '11px -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif';
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';
  
  for (let i = 0; i <= 5; i++) {
    const val = minVal + (i / 5) * (maxVal - minVal);
    const yPos = getY(val);
    ctx.beginPath();
    ctx.moveTo(padding.left, yPos);
    ctx.lineTo(padding.left + plotW, yPos);
    ctx.stroke();
    ctx.fillText(formatUSD(val), padding.left - 10, yPos);
  }
  
  // Zero Line
  if (minVal < 0 && maxVal > 0) {
    const zeroY = getY(0);
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 59, 48, 0.6)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padding.left, zeroY);
    ctx.lineTo(padding.left + plotW, zeroY);
    ctx.stroke();
    ctx.fillStyle = '#FF3B30';
    ctx.textAlign = 'left';
    ctx.fillText('$0 Depletion Line', padding.left + plotW - 95, zeroY - 8);
    ctx.restore();
  }
  
  // X Axis Month Ticks
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  ctx.fillStyle = '#86868B';
  for (let m = 0; m <= 24; m += 3) {
    ctx.fillText(`M${m}`, getX(m), padding.top + plotH + 10);
  }
  
  // Smooth Bezier Curve of Cash
  const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + plotH);
  gradient.addColorStop(0, 'rgba(0, 113, 227, 0.16)');
  gradient.addColorStop(1, 'rgba(0, 113, 227, 0.0)');
  
  ctx.beginPath();
  ctx.moveTo(getX(0), getY(0));
  ctx.lineTo(getX(0), getY(history[0].cash));
  for (let m = 1; m <= 24; m++) {
    const prevX = getX(m - 1);
    const prevY = getY(history[m - 1].cash);
    const currX = getX(m);
    const currY = getY(history[m].cash);
    const midX = (prevX + currX) / 2;
    ctx.bezierCurveTo(midX, prevY, midX, currY, currX, currY);
  }
  ctx.lineTo(getX(24), getY(0));
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();
  
  // Curve Stroke
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
  ctx.stroke();
  
  // Points
  for (let m = 0; m <= 24; m += 2) {
    ctx.beginPath();
    ctx.arc(getX(m), getY(history[m].cash), 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#FFFFFF';
    ctx.fill();
    ctx.strokeStyle = '#0071E3';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  
  // Active Hover Point
  if (state.hoveredMonthIndex !== null && state.hoveredMonthIndex >= 0 && state.hoveredMonthIndex <= 24) {
    const m = state.hoveredMonthIndex;
    const xPos = getX(m);
    const yPos = getY(history[m].cash);
    
    ctx.save();
    ctx.strokeStyle = 'rgba(0, 113, 227, 0.4)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(xPos, padding.top);
    ctx.lineTo(xPos, padding.top + plotH);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.arc(xPos, yPos, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#0071E3';
    ctx.fill();
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();
  }
  
  ctx.restore();
}

// Pointer / Hover Interaction
function handleCanvasPointer(e) {
  const canvas = DOM.canvas;
  const rect = canvas.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  
  const x = clientX - rect.left;
  const padding = { top: 25, right: 30, bottom: 40, left: 70 };
  const plotW = rect.width - padding.left - padding.right;
  
  if (x < padding.left || x > rect.width - padding.right) {
    DOM.tooltip.style.display = 'none';
    state.hoveredMonthIndex = null;
    drawRealChart(computeRealSimulation());
    return;
  }
  
  const normalized = (x - padding.left) / plotW;
  const month = Math.min(24, Math.max(0, Math.round(normalized * 24)));
  state.hoveredMonthIndex = month;
  
  const sim = computeRealSimulation();
  const data = sim.history[month];
  
  DOM.tooltip.innerHTML = `
    <div class="tooltip-month">Month ${month}</div>
    <div class="tooltip-row">
      <span style="color:#A1A1A6">Reserve Balance</span>
      <span class="tooltip-val" style="color:#FFFFFF">${formatUSD(data.cash)}</span>
    </div>
    <div class="tooltip-row">
      <span style="color:#A1A1A6">Net Take-Home</span>
      <span class="tooltip-val" style="color:#32D74B">${formatUSD(data.inflow)}</span>
    </div>
    <div class="tooltip-row">
      <span style="color:#A1A1A6">Total Living Burn</span>
      <span class="tooltip-val" style="color:#FF6961">${formatUSD(data.burn)}</span>
    </div>
    <div class="tooltip-row" style="border-top: 1px solid rgba(255,255,255,0.15); margin-top:4px; padding-top:4px;">
      <span style="color:#A1A1A6">Monthly Delta</span>
      <span class="tooltip-val" style="color:${data.netFlow >= 0 ? '#32D74B' : '#FF6961'}">${(data.netFlow >= 0 ? '+' : '') + formatUSD(data.netFlow)}/mo</span>
    </div>
  `;
  
  DOM.tooltip.style.display = 'block';
  DOM.tooltip.style.left = `${clientX - rect.left}px`;
  DOM.tooltip.style.top = `${Math.max(10, clientY - rect.top - 15)}px`;
  
  drawRealChart(sim);
}

function handlePointerLeave() {
  DOM.tooltip.style.display = 'none';
  state.hoveredMonthIndex = null;
  drawRealChart(computeRealSimulation());
}

// Attach Events
function attachEvents() {
  DOM.wageRange.addEventListener('input', (e) => {
    state.annualGross = parseFloat(e.target.value);
    render();
  });
  
  DOM.savingsRange.addEventListener('input', (e) => {
    state.initialSavings = parseFloat(e.target.value);
    render();
  });
  
  DOM.discretionaryRange.addEventListener('input', (e) => {
    state.discretionaryMonthly = parseFloat(e.target.value);
    render();
  });
  
  DOM.metroSelect.addEventListener('change', (e) => {
    state.selectedMetro = e.target.value;
    const metro = REAL_DATA.metros[state.selectedMetro];
    state.annualGross = metro.blsWages.p50_median;
    DOM.wageRange.value = state.annualGross;
    DOM.metroPills.forEach(pill => {
      pill.classList.toggle('active', pill.dataset.metro === state.selectedMetro);
    });
    render();
  });
  
  DOM.metroPills.forEach(pill => {
    pill.addEventListener('click', () => {
      state.selectedMetro = pill.dataset.metro;
      DOM.metroSelect.value = state.selectedMetro;
      const metro = REAL_DATA.metros[state.selectedMetro];
      state.annualGross = metro.blsWages.p50_median;
      DOM.wageRange.value = state.annualGross;
      DOM.metroPills.forEach(p => p.classList.toggle('active', p === pill));
      render();
    });
  });
  
  DOM.housingRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
      if (e.target.checked) {
        state.housingType = e.target.value;
        render();
      }
    });
  });
  
  DOM.pivotToggle.addEventListener('change', (e) => {
    state.isCareerPivot = e.target.checked;
    render();
  });
  
  DOM.eraSelect.addEventListener('change', (e) => {
    state.selectedEra = e.target.value;
    render();
  });
  
  DOM.canvas.addEventListener('mousemove', handleCanvasPointer);
  DOM.canvas.addEventListener('mouseleave', handlePointerLeave);
  DOM.canvas.addEventListener('touchmove', handleCanvasPointer, { passive: true });
  DOM.canvas.addEventListener('touchend', handlePointerLeave);
  
  window.addEventListener('resize', () => render());
  
  if (DOM.btnReset) {
    DOM.btnReset.addEventListener('click', () => {
      state.selectedMetro = 'san_francisco';
      state.annualGross = 178900;
      state.housingType = 'oneBed';
      state.initialSavings = 35000;
      state.discretionaryMonthly = 1200;
      state.isCareerPivot = false;
      DOM.wageRange.value = state.annualGross;
      DOM.savingsRange.value = state.initialSavings;
      DOM.discretionaryRange.value = state.discretionaryMonthly;
      DOM.metroSelect.value = 'san_francisco';
      DOM.pivotToggle.checked = false;
      DOM.metroPills.forEach(p => p.classList.toggle('active', p.dataset.metro === 'san_francisco'));
      render();
    });
  }
  
  if (DOM.btnExport) {
    DOM.btnExport.addEventListener('click', () => window.print());
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initDOM();
  attachEvents();
  render();
});
"""

with open("app.js", "w") as f:
    f.write(js_code)

print("generate_app_js.py completed successfully!")
