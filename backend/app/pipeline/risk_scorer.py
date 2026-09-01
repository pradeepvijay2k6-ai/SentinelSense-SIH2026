"""
Multimodal Fusion & Explainable Risk Scoring Engine for SentinelSense.
SIH 2026 Problem Statement 26186 (Predictive Stress & Welfare Monitoring for CAPF).

Fuses:
1. Sleep Architecture Degradation Score (0-100)
2. Autonomic Cardiovascular Stress Score (0-100)
3. Nocturnal Hypoxemia / Apnea Score (0-100)
4. Actigraphy Restlessness Score (0-100)

Produces:
- Composite Fatigue & Stress Risk Score (0-100)
- Operational Risk Level (LOW, MODERATE, HIGH)
- Tactical Readiness Verdict (Fit for Duty, Monitoring Required, Tactical Rest Recommended, Unfit for High-Stress Ops)
- Explainable AI Clinical Insights & Commander Action Points
"""

from typing import Dict, Any, List, Tuple
import numpy as np

def compute_multimodal_risk_scores(
    sleep_metrics: Dict[str, Any],
    hrv_metrics: Dict[str, Any],
    spo2_metrics: Dict[str, Any],
    motion_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes weighted multimodal fusion scores and plain-language explainability narratives.
    """
    # 1. Sleep Quality Degradation Score (0 = perfect sleep, 100 = severe deficit)
    # Normative benchmarks: Efficiency >85%, Deep N3 >15%, REM >18%, Wake <15%
    eff = sleep_metrics.get("sleep_efficiency", 85.0)
    deep = sleep_metrics.get("deep_sleep_pct", 20.0)
    rem = sleep_metrics.get("rem_sleep_pct", 20.0)
    wake = sleep_metrics.get("wake_pct", 10.0)
    
    eff_deficit = max(0.0, (85.0 - eff) * 1.6)
    deep_deficit = max(0.0, (18.0 - deep) * 4.0)
    rem_deficit = max(0.0, (18.0 - rem) * 2.5)
    wake_excess = max(0.0, (wake - 15.0) * 1.5)
    
    sleep_score = float(np.clip(eff_deficit * 0.40 + deep_deficit * 0.30 + rem_deficit * 0.15 + wake_excess * 0.15, 0, 100))
    
    # 2. Autonomic Cardiovascular Stress Score (0 = calm/restored, 100 = severe sympathetic strain)
    # Normative benchmarks: RMSSD >45ms (healthy vagal tone), Baevsky <100, LF/HF <2.0, HR 50-70 bpm
    rmssd = hrv_metrics.get("hrv_rmssd", 45.0)
    baevsky = hrv_metrics.get("baevsky_stress_index", 90.0)
    lf_hf = hrv_metrics.get("hrv_lf_hf_ratio", 1.5)
    avg_hr = hrv_metrics.get("avg_heart_rate", 62.0)
    
    rmssd_deficit = max(0.0, (48.0 - rmssd) * 2.8)
    baevsky_pts = min(100.0, (baevsky - 70.0) * 0.35) if baevsky > 70 else 0.0
    lf_hf_pts = min(100.0, max(0.0, (lf_hf - 1.8) * 25.0))
    hr_excess = max(0.0, (avg_hr - 68.0) * 2.5) if avg_hr > 68 else 0.0
    
    stress_score = float(np.clip(rmssd_deficit * 0.35 + baevsky_pts * 0.30 + lf_hf_pts * 0.20 + hr_excess * 0.15, 0, 100))
    
    # 3. Nocturnal Hypoxia Score (0 = clear airway, 100 = severe desaturations)
    # Normative benchmarks: ODI <5 dips/hr (normal), 5-15 (mild), 15-30 (moderate), >30 (severe)
    odi = spo2_metrics.get("odi_dips_per_hour", 0.0)
    min_spo2 = spo2_metrics.get("spo2_min", 96.0)
    hypoxic_burden = spo2_metrics.get("hypoxic_burden_pct", 0.0)
    
    odi_pts = min(100.0, odi * 4.5)
    min_spo2_pts = max(0.0, (93.0 - min_spo2) * 7.0) if min_spo2 < 93.0 else 0.0
    burden_pts = min(100.0, hypoxic_burden * 5.0)
    
    hypoxia_score = float(np.clip(odi_pts * 0.50 + min_spo2_pts * 0.35 + burden_pts * 0.15, 0, 100))
    
    # 4. Restlessness / Actigraphy Score (0 = calm, 100 = highly agitated)
    restlessness = motion_metrics.get("restlessness_index", 5.0)
    restless_score = float(np.clip(restlessness * 1.8, 0, 100))
    
    # Combined Fatigue Score
    fatigue_score = float(np.clip(sleep_score * 0.65 + restless_score * 0.35, 0, 100))
    
    # Composite Sentinel Fatigue & Stress Risk Score (0-100)
    base_composite = (
        stress_score * 0.35 +
        sleep_score * 0.35 +
        hypoxia_score * 0.15 +
        restless_score * 0.15
    )
    max_domain = max(sleep_score, stress_score, hypoxia_score, fatigue_score)
    composite_risk_score = round(float(np.clip(0.65 * base_composite + 0.35 * max_domain, 0, 100)), 1)
    
    # Risk Level Categorization
    if composite_risk_score <= 30.0:
        risk_level = "LOW"
        readiness_verdict = "Fit for Tactical Duty"
    elif composite_risk_score <= 60.0:
        risk_level = "MODERATE"
        readiness_verdict = "Elevated Fatigue Risk — Duty Monitoring Advised"
    else:
        risk_level = "HIGH"
        readiness_verdict = "Critical Fatigue & Stress — Tactical Rest Recommended"
        
    # Generate Key Risk Drivers
    key_drivers = []
    if rmssd < 28.0:
        key_drivers.append(f"Vagal suppression with low HRV RMSSD ({rmssd:.1f} ms, normal >45 ms)")
    if baevsky > 200.0:
        key_drivers.append(f"Sympathetic autonomic strain: Baevsky Stress Index ({baevsky:.0f}, normal <120)")
    if deep < 12.0:
        key_drivers.append(f"Deep Slow-Wave sleep deficit (N3: {deep:.1f}%, recommended 15-25%)")
    if eff < 75.0:
        key_drivers.append(f"Severely fragmented sleep architecture (Efficiency: {eff:.1f}%)")
    if odi >= 12.0:
        key_drivers.append(f"Frequent nocturnal oxygen desaturations (ODI: {odi:.1f} dips/hr, nadir {min_spo2:.0f}%)")
    if restlessness > 35.0:
        key_drivers.append(f"High motor restlessness & positional instability ({restlessness:.1f}% restless epochs)")
    if not key_drivers:
        key_drivers.append("Optimal restorative sleep architecture and balanced autonomic tone.")
        
    # Generate Plain-Language Clinical Explanation for Medical Officer
    clinical_explanation = (
        f"Physiological analysis indicates a Composite Risk Score of {composite_risk_score}/100 ({risk_level} band). "
        f"Autonomic assessment reveals a mean HR of {avg_hr:.0f} bpm, RMSSD of {rmssd:.1f} ms, and LF/HF ratio of {lf_hf:.2f}, "
        f"reflecting {'significant sympathetic predominance and reduced parasympathetic recovery' if stress_score > 50 else 'balanced autonomic regulation'}. "
        f"Sleep staging achieved {eff:.1f}% efficiency with {deep:.1f}% Stage N3 (slow-wave) and {rem:.1f}% REM sleep. "
        + (f"Oximetry recorded {odi:.1f} desaturation events/hr with a nadir of {min_spo2:.0f}%, indicating nocturnal airway compromise. " if odi >= 8.0 else "Oximetry remained stable with normal nocturnal oxygenation. ")
        + f"Actigraphy detected {restlessness:.1f}% motor restlessness during the recording period."
    )
    
    # Generate Actionable Tactical Briefing for Commander
    if risk_level == "LOW":
        commander_summary = (
            f"Personnel exhibits high operational readiness (Risk Score: {composite_risk_score}/100). "
            f"Physiological baseline shows full physical and mental recovery. Recommended for regular combat, QRT, or patrolling duty."
        )
        recommendations = [
            "Maintain current duty and rest schedule.",
            "Cleared for standard tactical and armed deployment.",
            "Routine periodic biometric monitoring recommended."
        ]
    elif risk_level == "MODERATE":
        commander_summary = (
            f"Personnel exhibits moderate fatigue/stress accumulation (Risk Score: {composite_risk_score}/100). "
            f"Restorative sleep deficit detected. Performance in prolonged cognitive or high-vigilance sentry duty may be impaired."
        )
        recommendations = [
            "Limit consecutive night-shift or high-intensity sentry assignments.",
            "Ensure a minimum uninterrupted 7-hour rest window before next deployment.",
            "Monitor hydration and schedule non-critical duty rotation if possible."
        ]
    else:
        commander_summary = (
            f"CRITICAL WARNING: High stress and fatigue risk detected (Risk Score: {composite_risk_score}/100). "
            f"Severe deficit in deep sleep recovery and high physiological strain. Acute risk of lapses in vigilance and delayed reaction time."
        )
        recommendations = [
            "Immediate relief from active armed duty / frontline convoy / QRT operations.",
            "Mandatory 24-hour restorative rest and recovery protocol.",
            "Medical Officer clinical consultation for autonomic stress and oximetry review.",
            "Re-evaluate physiological status prior to next operational clearance."
        ]
        
    return {
        "risk_score": composite_risk_score,
        "risk_level": risk_level,
        "readiness_verdict": readiness_verdict,
        "sleep_score": round(sleep_score, 1),
        "stress_score": round(stress_score, 1),
        "fatigue_score": round(fatigue_score, 1),
        "hypoxia_score": round(hypoxia_score, 1),
        "key_drivers": key_drivers,
        "clinical_explanation": clinical_explanation,
        "commander_summary": commander_summary,
        "recommendations": recommendations
    }
