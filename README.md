# Runway Studio — Interactive Decision & Capital Simulator

> **An interactive data visualization model for high-stakes career transitions, startup ventures, and personal financial decisions.**
> Designed strictly following **Apple Human Interface Guidelines (HIG)**: subtle typography, refined Cupertino color accents, zero neo/neon colors, and responsive retina graphics.

---

## 🎯 Executive Summary & Scenario Selection

### 1. The Decision Problem
One of the most consequential decisions people struggle with is the **Career Leap Dilemma**: *“Can I afford to leave my salaried role to pursue a new startup, creative studio, freelance career, or graduate degree without risking insolvency?”*

Without quantitative modeling, people rely on rough mental math or anxiety-driven guesses. **Runway Studio** eliminates ambiguity by modeling the trajectory of capital reserves across a 24-month horizon based on real-world levers.

---

## 📋 Step-by-Step Guide Checklist

### Phase I: Pick Your Scenario
- [x] **Choose your scenario**: Career Pivot & Financial Runway Decision Engine (*Can I afford to make the leap?*).
- [x] **Decide which variables matter**:
  1. **Initial Cash Reserves ($)**: Liquid seed capital available on Day 1.
  2. **Baseline Monthly Burn ($/mo)**: Non-negotiable living expenses (rent, food, healthcare, utilities).
  3. **Target Monthly Income ($/mo)**: Expected steady-state revenue from contracts, venture, or product sales.
  4. **Revenue Ramp Horizon (Months)**: Time required to progress from $0 to full target revenue.
  5. **Contingency / Tax Buffer (+18%)**: Self-employment tax and unexpected medical/operational overhead.
  6. **Side-Income Floor (+$1,200/mo)**: Guaranteed baseline buffer (tutoring, advisory, part-time contract).

---

### Phase II: Build the Data Visualization
- [x] **Build the data visualization**: Structured into a reactive single-page application (`index.html`, `styles.css`, `app.js`).
- [x] **Adjust the variables to refine the visualization**: Implemented real-time linear interpolation, dual-band revenue/burn indicators, and smooth Bezier splines.
- [x] **Test each slider**:
  - *Savings Slider* ($5,000 – $150,000)
  - *Monthly Burn Slider* ($1,200 – $12,000)
  - *Target Revenue Slider* ($0 – $20,000)
  - *Ramp Speed Slider* (1 – 18 months)
  - *Dual Safeguard Toggles* (Tax contingency & side income)
- [x] **Restyle it**:
  - Implemented Apple UI/UX Pro design language:
    - Neutral canvas (`#F5F5F7`), pure white cards (`#FFFFFF`), micro-borders (`rgba(0,0,0,0.07)`).
    - Apple System Blue (`#0071E3`), subtle Emerald (`#34C759`), Amber warning (`#FF9500`), and Coral red (`#FF3B30`).
    - **Strictly zero neon / neo-brutalist styling**.
    - Retina-scaled HTML5 Canvas with dynamic crosshair hover inspection and floating frosted-glass tooltip.

---

### Phase III: Check That It Holds Up
- [x] **Run a real scenario and sanity-check the math**:
  - Real Scenario Tested: **Tech Venture Leap**
    - Starting Capital: **$38,000**
    - Monthly Burn: **$3,800/mo** + 18% tax buffer = **$4,484/mo**
    - Target Revenue: **$6,000/mo** ramping over **7 months**
    - **Result**:
      - Break-Even Month reached in **Month 6** ($5,142.86 > $4,484)
      - Minimum Capital Trough: **$28,437** (Lowest dip in Month 6)
      - 24-Month Ending Balance: **$56,384** (Net Gain of **+$18,384**)
      - Runway: **Infinite / Self-Sustaining**
  - Edge Case Tested: **Zero Revenue ($20,000 savings @ $2,000/mo burn)**
    - Exact mathematical depletion: $20,000 / $2,000 = **10.0 months** (Validated to 0.001 precision).

---

## 🧮 Quantitative Mathematical Model

For any given month $m \in \{0, 1, 2, \dots, 24\}$:

1. **Effective Monthly Burn ($B_m$)**:
   $$\text{Burn}_m = \text{BaseBurn} \times (1 + \text{TaxBufferRate})$$

2. **Total Monthly Revenue ($R_m$)**:
   $$R_m = \begin{cases} 
   0 & \text{if } m = 0 \\
   \text{TargetRevenue} \times \left(\frac{m}{\text{RampMonths}}\right) + \text{SideIncome} & \text{if } 1 \le m \le \text{RampMonths} \\
   \text{TargetRevenue} + \text{SideIncome} & \text{if } m > \text{RampMonths}
   \end{cases}$$

3. **Monthly Net Cash Flow ($\Delta C_m$)**:
   $$\Delta C_m = R_m - B_m$$

4. **Discrete Cash Ledger ($C_m$)**:
   $$C_0 = \text{InitialReserves}$$
   $$C_m = C_{m-1} + \Delta C_m = C_0 + \sum_{k=1}^m (R_k - B_k)$$

5. **Fractional Zero-Depletion Interpolation**:
   If $C_k \le 0$ at month $k$:
   $$\text{Runway} = (k - 1) + \frac{C_{k-1}}{C_{k-1} - C_k}$$

---

## 🚀 How to Run Locally

You can open `index.html` directly in any modern browser:

### Option A: Direct Open
Double click `index.html` or open it with macOS Chrome/Safari:
```bash
open index.html
```

### Option B: Local HTTP Server
Run a local static server from this folder:
```bash
python3 -m http.server 8085
```
Then visit `http://localhost:8085` in your browser.

---

## 🎨 UI/UX Features
- **Instant Reactive Updates**: Sliders use hardware-accelerated canvas redraws on every input event (0ms latency).
- **Interactive Tooltip**: Hovering across any month highlights the data point, displays exact bank balance, monthly burn, revenue, and net delta.
- **Decision Presets**: Includes 4 pre-configured real scenarios:
  1. *Tech Venture Leap*
  2. *Campus to Studio*
  3. *Higher Ed Pivot*
  4. *Cautious Safety*
- **Export & Print**: Clean `@media print` CSS formats the entire dashboard into an executive 1-page PDF decision report.

