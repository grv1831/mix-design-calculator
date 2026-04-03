"""
Concrete Mix Design — IS 10262 : 2019
Absolute Volume Method
"""

from reference_data import (
    SD_TABLE, EXPOSURE_TABLE, WATER_CONTENT_TABLE, CA_VOLUME_TABLE
)


class MixDesign:
    def __init__(self, grade, exposure, agg_size, fa_zone, slump,
                 admixture, sg_cement, sg_fa, sg_ca, air_pct, n_samples):
        self.grade      = grade
        self.exposure   = exposure
        self.agg_size   = agg_size
        self.fa_zone    = fa_zone
        self.slump      = slump
        self.admixture  = admixture
        self.sg_cement  = sg_cement
        self.sg_fa      = sg_fa
        self.sg_ca      = sg_ca
        self.air_pct    = air_pct
        self.n_samples  = n_samples

    # ── Step 1 ──────────────────────────────────────────────────────────────
    def target_strength(self):
        sd = SD_TABLE.get(self.grade, 5.0)
        t  = 1.65
        return round(self.grade + t * sd, 2), sd

    # ── Step 2 ──────────────────────────────────────────────────────────────
    def water_cement_ratio(self, fck_target):
        max_wc = EXPOSURE_TABLE[self.exposure]["max_wc"]
        # IS 10262 Cl. 5.1: adopt w/c from IS 456 Table 5 (exposure governs).
        # Additionally verify against strength using Abrams' approximation.
        strength_wc = round(min(max_wc, 27 / (fck_target + 13.5)), 2)
        design_wc   = min(max_wc, strength_wc)
        design_wc   = round(max(design_wc, 0.35), 2)   # practical lower bound
        design_wc   = round(min(design_wc, max_wc), 2)
        return design_wc, max_wc

    # ── Step 3 ──────────────────────────────────────────────────────────────
    def water_content(self):
        base = WATER_CONTENT_TABLE[self.agg_size][self.slump]
        if self.admixture == "plasticizer":
            base = round(base * 0.90)
        elif self.admixture == "superplasticizer":
            base = round(base * 0.80)
        return base

    # ── Step 4 ──────────────────────────────────────────────────────────────
    def cement_content(self, water, wc):
        cement_raw = round(water / wc)
        min_cement = EXPOSURE_TABLE[self.exposure]["min_cement"]
        cement     = max(cement_raw, min_cement)
        adjusted   = cement != cement_raw
        return cement, cement_raw, adjusted

    # ── Step 5 ──────────────────────────────────────────────────────────────
    def ca_content(self):
        vol_frac = CA_VOLUME_TABLE[self.agg_size][self.fa_zone]
        # Correction for slump > 75 mm: reduce CA fraction by 0.01
        if self.slump == 125:
            vol_frac = round(vol_frac - 0.01, 2)
        ca = round(vol_frac * self.sg_ca * 1000)
        return ca, vol_frac

    # ── Step 6 ──────────────────────────────────────────────────────────────
    def fa_content(self, cement, water, ca):
        air = self.air_pct / 100
        vol_cement = cement / (self.sg_cement * 1000)
        vol_water  = water  / 1000
        vol_ca     = ca     / (self.sg_ca * 1000)
        vol_fa     = 1 - vol_cement - vol_water - vol_ca - air
        fa = round(vol_fa * self.sg_fa * 1000)
        return fa, vol_cement, vol_water, vol_ca, vol_fa

    # ── Main ────────────────────────────────────────────────────────────────
    def calculate(self):
        fck_target, sd = self.target_strength()
        wc, max_wc     = self.water_cement_ratio(fck_target)
        water          = self.water_content()
        cement, cement_raw, adjusted = self.cement_content(water, wc)
        ca, ca_vol_frac= self.ca_content()
        fa, vol_cement, vol_water, vol_ca, vol_fa = self.fa_content(cement, water, ca)

        air     = self.air_pct / 100
        vol_air = air

        total = cement + water + fa + ca

        return {
            "fck_target":      fck_target,
            "sd":              sd,
            "wc":              wc,
            "max_wc":          max_wc,
            "water":           water,
            "cement":          cement,
            "cement_raw":      cement_raw,
            "cement_adjusted": adjusted,
            "ca":              ca,
            "ca_vol_frac":     ca_vol_frac,
            "fa":              fa,
            "total":           total,
            "vol_cement":      round(vol_cement, 4),
            "vol_water":       round(vol_water,  4),
            "vol_ca":          round(vol_ca,     4),
            "vol_fa":          round(vol_fa,     4),
            "vol_air":         round(vol_air,    4),
            "ratio_fa":        round(fa / cement, 2),
            "ratio_ca":        round(ca / cement, 2),
            "min_cement":      EXPOSURE_TABLE[self.exposure]["min_cement"],
        }

    # ── Step text for Tab 2 ─────────────────────────────────────────────────
    def get_steps(self, res):
        admix_note = ""
        if self.admixture == "plasticizer":
            admix_note = " (reduced 10% for plasticizer)"
        elif self.admixture == "superplasticizer":
            admix_note = " (reduced 20% for superplasticizer)"

        slump_label = {25: "25 mm (stiff)", 75: "50–100 mm (medium)",
                       125: "100–150 mm (high)"}[self.slump]

        return [
            {
                "title":       "Target Mean Compressive Strength",
                "description": (
                    f"f'ck = fck + t × s, where s = standard deviation for M{self.grade} "
                    f"= {res['sd']} MPa and t = 1.65 (for p = 5% defective results)"
                ),
                "formula":     f"f'ck = {self.grade} + 1.65 × {res['sd']} = {res['fck_target']} MPa",
                "result":      f"Target mean strength = {res['fck_target']} MPa",
            },
            {
                "title":       "Water-Cement Ratio",
                "description": (
                    f"From IS 456 Table 5, max w/c for {self.exposure.replace('_',' ')} "
                    f"exposure = {res['max_wc']}. Design w/c computed and checked against limit."
                ),
                "formula":     f"Design w/c = min({res['max_wc']}, computed) = {res['wc']}",
                "result":      f"Adopted w/c = {res['wc']}",
            },
            {
                "title":       "Water Content",
                "description": (
                    f"From IS 10262 Table 2 for {self.agg_size} mm aggregate "
                    f"and {slump_label} slump{admix_note}."
                ),
                "formula":     f"Free water content = {res['water']} liters/m³",
                "result":      f"Water = {res['water']} liters/m³",
            },
            {
                "title":       "Cement Content",
                "description": (
                    f"Cement = Water / w/c. Checked against minimum cement content "
                    f"({res['min_cement']} kg/m³) for {self.exposure.replace('_',' ')} exposure (IS 456 Table 5)."
                ),
                "formula":     (
                    f"Cement = {res['water']} / {res['wc']} = {res['cement_raw']} kg/m³"
                    + (f"  →  Raised to {res['cement']} kg/m³ (min. requirement)"
                       if res['cement_adjusted'] else "")
                ),
                "result":      f"Cement = {res['cement']} kg/m³",
            },
            {
                "title":       "Coarse Aggregate Content",
                "description": (
                    f"From IS 10262 Table 3: volume fraction for {self.agg_size} mm "
                    f"aggregate with Zone {self.fa_zone} FA = {res['ca_vol_frac']}."
                ),
                "formula":     (
                    f"CA = {res['ca_vol_frac']} × {self.sg_ca} × 1000 = {res['ca']} kg/m³"
                ),
                "result":      f"Coarse aggregate = {res['ca']} kg/m³",
            },
            {
                "title":       "Fine Aggregate Content (Absolute Volume Method)",
                "description": (
                    "The sum of absolute volumes of all ingredients must equal 1 m³. "
                    "Fine aggregate occupies the remaining volume."
                ),
                "formula":     (
                    f"Vol. cement={res['vol_cement']}  +  Vol. water={res['vol_water']}  +  "
                    f"Vol. CA={res['vol_ca']}  +  Air={res['vol_air']}\n"
                    f"Vol. FA = 1 − {round(res['vol_cement']+res['vol_water']+res['vol_ca']+res['vol_air'],4)} "
                    f"= {res['vol_fa']} m³\n"
                    f"FA = {res['vol_fa']} × {self.sg_fa} × 1000 = {res['fa']} kg/m³"
                ),
                "result":      f"Fine aggregate = {res['fa']} kg/m³",
            },
            {
                "title":       "Final Mix Proportions",
                "description": "Express all quantities relative to one part cement by weight.",
                "formula":     (
                    f"Cement : FA : CA = 1 : {res['ratio_fa']} : {res['ratio_ca']}\n"
                    f"w/c = {res['wc']}\n"
                    f"Water = {res['water']} liters/m³"
                ),
                "result":      f"Mix ratio = 1 : {res['ratio_fa']} : {res['ratio_ca']}",
            },
        ]
