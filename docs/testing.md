# Automated Testing & Verification Documentation

This document describes the automated test architecture, coverage, validation criteria, and physical invariant checks implemented in the **Factory Energy Intelligence & Optimization Platform**.

---

## 1. Test Architecture & Execution

The testing suite is implemented with `pytest` and structured into two automated test modules:

1. **`tests/test_calculations.py`**: Rigorous unit tests for three-phase electrical formulas, IEEE/NEMA phase unbalance, Joule cable loss models, discrete energy integrals, SEC calculations, electricity tariffs, and CEA carbon accounting.
2. **`tests/test_scenarios.py`**: Scenario-based integration tests verifying the 8 challenge test requirements.

### Running the Test Suite
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run only electrical calculation tests
pytest tests/test_calculations.py -v

# Run only scenario verification tests
pytest tests/test_scenarios.py -v
```

---

## 2. Test Coverage & Validation Matrix

| Test ID | Module | Verification Scope | Status | Expected Outcome |
|---|---|---|---|---|
| `test_three_phase_power_balanced` | `test_calculations` | $S = \sqrt{3} V I$, $P = S \times \text{PF}$, $Q = \sqrt{S^2 - P^2}$ | **PASSED** | Exact physical triangle balance |
| `test_power_factor_clamping` | `test_calculations` | Boundary checks for $\text{PF} \in [0.01, 1.0]$ | **PASSED** | Clamped to realistic bounds |
| `test_nema_phase_imbalance_normal` | `test_calculations` | Balanced 3-phase currents ($100, 101, 99$ A) | **PASSED** | $\text{Imbalance} = 1.0\%$, severity `NORMAL` |
| `test_nema_phase_imbalance_critical`| `test_calculations` | High deviation ($120, 90, 90$ A) | **PASSED** | $\text{Imbalance} = 20.0\%$, severity `CRITICAL` |
| `test_feeder_cable_loss_and_resistivity` | `test_calculations` | $R = \rho_{50} L / A$ and $P_{\text{loss}} = 3 I^2 R$ | **PASSED** | Exact match with theoretical Joule dissipation |
| `test_discrete_energy_integral` | `test_calculations` | $E = \sum P_i \Delta t$ (60 kW over 12 $\times$ 5-min steps) | **PASSED** | Energy equals exactly 60.0 kWh |
| `test_sec_calculation_and_improvement` | `test_calculations` | $\text{SEC} = E / \text{Prod}$ and % improvement | **PASSED** | $0.50 \to 0.425 \text{ kWh/unit} = 15.0\%$ gain |
| `test_carbon_emissions_cea_factor` | `test_calculations` | CEA India factor $0.716\text{ kg CO}_2\text{/kWh}$ | **PASSED** | Exact Scope 2 emissions |
| `test_cost_model_tariff_slots` | `test_calculations` | Off-peak, Normal, and Peak TOD pricing | **PASSED** | Correct itemized energy billing |
| `test_scenario_1_normal_operation` | `test_scenarios` | Healthy telemetry at nominal rated load | **PASSED** | Zero critical alerts, Health $\ge 80$ |
| `test_scenario_2_motor_energy_increase`| `test_scenarios` | Power $+18\%$ without production change | **PASSED** | `MACHINE_EFFICIENCY_DEGRADATION` triggered |
| `test_scenario_3_production_decrease_sec_increase` | `test_scenarios` | Energy constant, production drops by 50% | **PASSED** | SEC doubles from 0.50 to 1.00 kWh/unit |
| `test_scenario_4_machine_on_zero_production_idle` | `test_scenarios` | Compressor running unloaded ($18.5\text{ kW}$, $\text{Prod} = 0$) | **PASSED** | `EXCESSIVE_IDLE_CONSUMPTION` alert |
| `test_scenario_5_phase_imbalance_alert`| `test_scenarios` | $I_r, I_y, I_b$ diverge ($18.5\%$ unbalance) | **PASSED** | `PHASE_IMBALANCE` critical alert |
| `test_scenario_6_low_power_factor_warning` | `test_scenarios` | Power factor drops to $0.72\text{ lag}$ | **PASSED** | `LOW_POWER_FACTOR` critical alert |
| `test_scenario_7_peak_period_load_recommendation` | `test_scenarios` | Thermal furnace in Peak slot (18:00–22:00) | **PASSED** | TOD Tariff Load Shifting SOP generated |
| `test_scenario_8_optimized_operation_production_constraint` | `test_scenarios` | Full optimization pass on sample batch | **PASSED** | Production invariant, SEC improves, comparison generated |

---

## 3. Physical Invariant Guarantees

Every optimization pass automatically enforces these invariant properties:

1. **Production Throughput Invariance**:
   $$\text{Production}_{\text{optimized}} \ge \text{Production}_{\text{baseline}} - \epsilon \quad (\epsilon = 0.01)$$
2. **Apparent Power Dominance**:
   $$S \ge P \quad \forall t$$
3. **Power Factor Bounds**:
   $$0.01 \le \text{PF} \le 1.00$$
4. **Non-Negative Cable Losses**:
   $$P_{\text{loss}} \ge 0.00\text{ kW}$$
