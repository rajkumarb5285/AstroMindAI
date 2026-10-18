from typing import Any

from typing_extensions import TypedDict


class KootaScore(TypedDict):
    koota_name: str
    max_points: float
    points_obtained: float
    description: str
    status: str  # 'auspicious', 'neutral', 'dosha', 'cancelled'
    cancellation_reason: str | None


class CompatibilityResult(TypedDict):
    total_points: float
    max_points: float
    percentage: float
    verdict: str  # 'Excellent', 'Good', 'Average', 'Inauspicious'
    kootas: list[KootaScore]
    doshas: list[str]
    cancellations: list[str]
    bride_summary: dict[str, Any]
    groom_summary: dict[str, Any]


# NAKSHATRA PROPERTIES REGISTRY (1-indexed, 1=Ashwini to 27=Revati)
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Gana: Deva (D), Manushya (M), Rakshasa (R)
NAKSHATRA_GANA = {
    1: "Deva", 2: "Manushya", 3: "Rakshasa", 4: "Manushya", 5: "Deva", 6: "Manushya",
    7: "Deva", 8: "Deva", 9: "Rakshasa", 10: "Rakshasa", 11: "Manushya", 12: "Manushya",
    13: "Deva", 14: "Rakshasa", 15: "Deva", 16: "Rakshasa", 17: "Deva", 18: "Rakshasa",
    19: "Rakshasa", 20: "Manushya", 21: "Manushya", 22: "Deva", 23: "Rakshasa", 24: "Rakshasa",
    25: "Manushya", 26: "Manushya", 27: "Deva",
}

# Nadi: Adi (1), Madhya (2), Antya (3)
NAKSHATRA_NADI = {
    1: "Adi", 2: "Madhya", 3: "Antya", 4: "Antya", 5: "Madhya", 6: "Adi",
    7: "Adi", 8: "Madhya", 9: "Antya", 10: "Antya", 11: "Madhya", 12: "Adi",
    13: "Adi", 14: "Madhya", 15: "Antya", 16: "Antya", 17: "Madhya", 18: "Adi",
    19: "Adi", 20: "Madhya", 21: "Antya", 22: "Antya", 23: "Madhya", 24: "Adi",
    25: "Adi", 26: "Madhya", 27: "Antya",
}

# Yoni Animals:
NAKSHATRA_YONI = {
    1: "Horse", 2: "Elephant", 3: "Sheep", 4: "Serpent", 5: "Serpent", 6: "Dog",
    7: "Cat", 8: "Sheep", 9: "Cat", 10: "Rat", 11: "Rat", 12: "Cow",
    13: "Buffalo", 14: "Tiger", 15: "Buffalo", 16: "Tiger", 17: "Deer", 18: "Deer",
    19: "Dog", 20: "Monkey", 21: "Mongoose", 22: "Monkey", 23: "Lion", 24: "Horse",
    25: "Lion", 26: "Cow", 27: "Elephant",
}

# Sworn Enemy Yoni pairs
ENEMY_YONIS = {
    frozenset({"Cow", "Tiger"}),
    frozenset({"Cat", "Rat"}),
    frozenset({"Serpent", "Mongoose"}),
    frozenset({"Dog", "Deer"}),
    frozenset({"Elephant", "Lion"}),
    frozenset({"Horse", "Buffalo"}),
    frozenset({"Monkey", "Sheep"}),
}

# Rashi Lords (Sign 1 to 12)
RASHI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

# Natural Planetary Relationships
PLANETARY_RELATIONS: dict[str, dict[str, list[str]]] = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "neutrals": ["Mercury"], "enemies": ["Venus", "Saturn"]},
    "Moon": {"friends": ["Sun", "Mercury"], "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": []},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "neutrals": ["Venus", "Saturn"], "enemies": ["Mercury"]},
    "Mercury": {"friends": ["Sun", "Venus"], "neutrals": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutrals": ["Saturn"], "enemies": ["Mercury", "Venus"]},
    "Venus": {"friends": ["Mercury", "Saturn"], "neutrals": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
    "Saturn": {"friends": ["Mercury", "Venus"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars"]},
}


def _get_planetary_relation(p1: str, p2: str) -> str:
    """Returns the relation of p1 towards p2."""
    if p1 == p2:
        return "same"
    rels = PLANETARY_RELATIONS.get(p1, {})
    if p2 in rels.get("friends", []):
        return "friend"
    if p2 in rels.get("neutrals", []):
        return "neutral"
    return "enemy"


def calculate_ashta_koota(
    bride_moon_sign: int,
    bride_nakshatra: int,
    bride_pada: int,
    groom_moon_sign: int,
    groom_nakshatra: int,
    groom_pada: int,
) -> CompatibilityResult:
    """
    Deterministically computes classical Parashari 36-point Ashta Koota matching.
    Includes comprehensive dosha detection (Nadi, Bhakoot, Gana) and classical cancellations.
    """
    doshas: list[str] = []
    cancellations: list[str] = []
    kootas: list[KootaScore] = []

    # 1. VARNA KOOTA (Max 1 point)
    # Brahmin: 4, 8, 12 (Rank 4) | Kshatriya: 1, 5, 9 (Rank 3) | Vaishya: 2, 6, 10 (Rank 2) | Shudra: 3, 7, 11 (Rank 1)
    def varna_rank(sign: int) -> int:
        if sign in [4, 8, 12]:
            return 4
        if sign in [1, 5, 9]:
            return 3
        if sign in [2, 6, 10]:
            return 2
        return 1

    b_v_rank = varna_rank(bride_moon_sign)
    g_v_rank = varna_rank(groom_moon_sign)
    if g_v_rank >= b_v_rank:
        varna_pts = 1.0
        v_desc = f"Groom varna rank ({g_v_rank}) is equal or higher than bride ({b_v_rank}). Full spiritual harmony."
        v_status = "auspicious"
    else:
        varna_pts = 0.0
        v_desc = f"Groom varna rank ({g_v_rank}) is lower than bride ({b_v_rank})."
        v_status = "neutral"

    kootas.append({
        "koota_name": "Varna",
        "max_points": 1.0,
        "points_obtained": varna_pts,
        "description": v_desc,
        "status": v_status,
        "cancellation_reason": None,
    })

    # 2. VASHYA KOOTA (Max 2 points)
    # Chatushpada: 1, 2, 9 (latter half), 10 (first half) -> 1, 2
    # Manava: 3, 6, 7, 9 (first half), 11 -> 3, 6, 7, 11
    # Jalachara: 4, 10 (latter half), 12 -> 4, 12
    # Vanachara: 5
    # Keeta: 8
    def vashya_cat(sign: int) -> str:
        if sign in [1, 2]:
            return "Chatushpada"
        if sign in [3, 6, 7, 11]:
            return "Manava"
        if sign in [4, 12]:
            return "Jalachara"
        if sign == 5:
            return "Vanachara"
        return "Keeta"

    b_vashya = vashya_cat(bride_moon_sign)
    g_vashya = vashya_cat(groom_moon_sign)
    if b_vashya == g_vashya:
        vashya_pts = 2.0
    elif (b_vashya, g_vashya) in [("Manava", "Chatushpada"), ("Chatushpada", "Manava")]:
        vashya_pts = 1.0
    elif (b_vashya, g_vashya) in [("Jalachara", "Keeta"), ("Keeta", "Jalachara")]:
        vashya_pts = 1.0
    elif b_vashya == "Vanachara" or g_vashya == "Vanachara":
        vashya_pts = 0.0
    else:
        vashya_pts = 0.5

    kootas.append({
        "koota_name": "Vashya",
        "max_points": 2.0,
        "points_obtained": vashya_pts,
        "description": f"Bride Vashya is {b_vashya}; Groom Vashya is {g_vashya}.",
        "status": "auspicious" if vashya_pts >= 1.5 else "neutral",
        "cancellation_reason": None,
    })

    # 3. TARA / DINA KOOTA (Max 3 points)
    # Count Nakshatras from Bride to Groom mod 9 and Groom to Bride mod 9
    b_to_g = ((groom_nakshatra - bride_nakshatra) % 27) % 9
    g_to_b = ((bride_nakshatra - groom_nakshatra) % 27) % 9
    # Auspicious remainders: 0 (9th Tara), 1, 2, 4, 6, 8. Inauspicious: 3 (Vipat), 5 (Pratyak), 7 (Naidhana)
    b_ok = b_to_g not in [3, 5, 7]
    g_ok = g_to_b not in [3, 5, 7]
    if b_ok and g_ok:
        tara_pts = 3.0
    elif b_ok or g_ok:
        tara_pts = 1.5
    else:
        tara_pts = 0.0

    kootas.append({
        "koota_name": "Tara",
        "max_points": 3.0,
        "points_obtained": tara_pts,
        "description": f"Dina Koota calculation: Bride-to-Groom Tara={b_to_g}; Groom-to-Bride Tara={g_to_b}.",
        "status": "auspicious" if tara_pts == 3.0 else ("neutral" if tara_pts > 0 else "dosha"),
        "cancellation_reason": None,
    })

    # 4. YONI KOOTA (Max 4 points)
    b_yoni = NAKSHATRA_YONI.get(bride_nakshatra, "Horse")
    g_yoni = NAKSHATRA_YONI.get(groom_nakshatra, "Horse")
    pair = frozenset({b_yoni, g_yoni})

    if b_yoni == g_yoni:
        yoni_pts = 4.0
        y_status = "auspicious"
    elif pair in ENEMY_YONIS:
        yoni_pts = 0.0
        y_status = "dosha"
        doshas.append(f"Vairi Yoni (Sworn Enemy animal pair: {b_yoni} vs {g_yoni})")
    else:
        # Friendly or neutral animals
        yoni_pts = 2.0
        y_status = "neutral"

    kootas.append({
        "koota_name": "Yoni",
        "max_points": 4.0,
        "points_obtained": yoni_pts,
        "description": f"Bride Yoni is {b_yoni}; Groom Yoni is {g_yoni}.",
        "status": y_status,
        "cancellation_reason": None,
    })

    # 5. GRAHA MAITRI (Max 5 points)
    b_lord = RASHI_LORDS.get(bride_moon_sign, "Mars")
    g_lord = RASHI_LORDS.get(groom_moon_sign, "Mars")
    b_rel = _get_planetary_relation(b_lord, g_lord)
    g_rel = _get_planetary_relation(g_lord, b_lord)

    if b_lord == g_lord or (b_rel == "friend" and g_rel == "friend"):
        maitri_pts = 5.0
    elif (b_rel == "friend" and g_rel == "neutral") or (b_rel == "neutral" and g_rel == "friend"):
        maitri_pts = 4.0
    elif b_rel == "neutral" and g_rel == "neutral":
        maitri_pts = 3.0
    elif (b_rel == "friend" and g_rel == "enemy") or (b_rel == "enemy" and g_rel == "friend"):
        maitri_pts = 1.0
    elif (b_rel == "neutral" and g_rel == "enemy") or (b_rel == "enemy" and g_rel == "neutral"):
        maitri_pts = 0.5
    else:
        maitri_pts = 0.0

    kootas.append({
        "koota_name": "Graha Maitri",
        "max_points": 5.0,
        "points_obtained": maitri_pts,
        "description": f"Rashi lords: Bride ({b_lord}), Groom ({g_lord}). Inter-planetary friendship score: {maitri_pts}/5.",
        "status": "auspicious" if maitri_pts >= 4.0 else ("neutral" if maitri_pts >= 1.0 else "dosha"),
        "cancellation_reason": None,
    })

    # 6. GANA KOOTA (Max 6 points)
    b_gana = NAKSHATRA_GANA.get(bride_nakshatra, "Deva")
    g_gana = NAKSHATRA_GANA.get(groom_nakshatra, "Deva")

    if b_gana == g_gana:
        gana_pts = 6.0
        g_status = "auspicious"
        g_cancel = None
    elif (b_gana == "Deva" and g_gana == "Manushya") or (b_gana == "Manushya" and g_gana == "Deva"):
        gana_pts = 5.0
        g_status = "auspicious"
        g_cancel = None
    else:
        # One is Rakshasa and the other is Deva or Manushya
        # Check classical Gana Dosha cancellation: If Moon sign lords are friends or same
        if b_lord == g_lord or (b_rel in ["friend", "same"] and g_rel in ["friend", "same"]):
            gana_pts = 5.0
            g_status = "cancelled"
            g_cancel = f"Gana Dosha cancelled: Rashi lords ({b_lord} and {g_lord}) are mutually friendly or identical."
            cancellations.append(g_cancel)
        else:
            gana_pts = 0.0
            g_status = "dosha"
            g_cancel = None
            doshas.append(f"Gana Dosha ({b_gana} and {g_gana})")

    kootas.append({
        "koota_name": "Gana",
        "max_points": 6.0,
        "points_obtained": gana_pts,
        "description": f"Bride Gana is {b_gana}; Groom Gana is {g_gana}.",
        "status": g_status,
        "cancellation_reason": g_cancel,
    })

    # 7. BHAKOOT KOOTA (Max 7 points)
    # Distance from Bride sign to Groom sign (1 to 12)
    b_to_g_dist = ((groom_moon_sign - bride_moon_sign) % 12) + 1
    # Dosha pairs: 2/12 (Dwirdwadashta), 6/8 (Shadashtaka), 9/5 (Navapanchaka)
    is_bhakoot_dosha = b_to_g_dist in [2, 6, 8, 9, 12]

    if not is_bhakoot_dosha:
        bhakoot_pts = 7.0
        bh_status = "auspicious"
        bh_cancel = None
    else:
        # Check classical Bhakoot cancellation:
        # 1. Both signs have the same lord (e.g. Aries-Scorpio, Taurus-Libra)
        # 2. Both sign lords are mutual friends
        if b_lord == g_lord:
            bhakoot_pts = 7.0
            bh_status = "cancelled"
            bh_cancel = f"Bhakoot Dosha ({b_to_g_dist}/{(14 - b_to_g_dist) % 12 or 12}) cancelled: Both signs share the same ruler ({b_lord})."
            cancellations.append(bh_cancel)
        elif b_rel in ["friend", "same"] and g_rel in ["friend", "same"]:
            bhakoot_pts = 7.0
            bh_status = "cancelled"
            bh_cancel = f"Bhakoot Dosha cancelled: Sign lords ({b_lord} and {g_lord}) are mutual friends."
            cancellations.append(bh_cancel)
        else:
            bhakoot_pts = 0.0
            bh_status = "dosha"
            bh_cancel = None
            doshas.append(f"Bhakoot Dosha (Moon sign relationship: {b_to_g_dist}th house)")

    kootas.append({
        "koota_name": "Bhakoot",
        "max_points": 7.0,
        "points_obtained": bhakoot_pts,
        "description": f"Moon sign axis is {b_to_g_dist}/{(14 - b_to_g_dist) % 12 or 12}.",
        "status": bh_status,
        "cancellation_reason": bh_cancel,
    })

    # 8. NADI KOOTA (Max 8 points)
    b_nadi = NAKSHATRA_NADI.get(bride_nakshatra, "Adi")
    g_nadi = NAKSHATRA_NADI.get(groom_nakshatra, "Madhya")

    if b_nadi != g_nadi:
        nadi_pts = 8.0
        n_status = "auspicious"
        n_cancel = None
    else:
        # Same Nadi: Check classical Nadi Dosha cancellations:
        # Cancellation 1: Different Rashi even if same Nakshatra (e.g. Krittika in Aries vs Taurus)
        # Cancellation 2: Different Nakshatra even if same Rashi
        # Cancellation 3: Same Nakshatra but different Padas
        if bride_moon_sign != groom_moon_sign:
            nadi_pts = 8.0
            n_status = "cancelled"
            n_cancel = f"Nadi Dosha ({b_nadi}) cancelled: Bride and Groom have different Moon signs."
            cancellations.append(n_cancel)
        elif bride_nakshatra != groom_nakshatra:
            nadi_pts = 8.0
            n_status = "cancelled"
            n_cancel = f"Nadi Dosha cancelled: Nakshatras differ despite sharing {b_nadi} Nadi."
            cancellations.append(n_cancel)
        elif bride_pada != groom_pada:
            nadi_pts = 8.0
            n_status = "cancelled"
            n_cancel = f"Nadi Dosha cancelled: Different Nakshatra Padas (Bride: {bride_pada}, Groom: {groom_pada})."
            cancellations.append(n_cancel)
        else:
            nadi_pts = 0.0
            n_status = "dosha"
            n_cancel = None
            doshas.append(f"Nadi Dosha ({b_nadi} Nadi clash without classical exception)")

    kootas.append({
        "koota_name": "Nadi",
        "max_points": 8.0,
        "points_obtained": nadi_pts,
        "description": f"Bride Nadi is {b_nadi}; Groom Nadi is {g_nadi}.",
        "status": n_status,
        "cancellation_reason": n_cancel,
    })

    # Summary calculations
    total_obtained = sum(k["points_obtained"] for k in kootas)
    max_pts = 36.0
    percentage = round((total_obtained / max_pts) * 100, 1)

    if total_obtained >= 28.0:
        verdict = "Excellent"
    elif total_obtained >= 18.0:
        verdict = "Good"
    elif total_obtained >= 12.0:
        verdict = "Average"
    else:
        verdict = "Inauspicious"

    return {
        "total_points": total_obtained,
        "max_points": max_pts,
        "percentage": percentage,
        "verdict": verdict,
        "kootas": kootas,
        "doshas": doshas,
        "cancellations": cancellations,
        "bride_summary": {
            "moon_sign": bride_moon_sign,
            "nakshatra_index": bride_nakshatra,
            "nakshatra_name": NAKSHATRA_NAMES[bride_nakshatra - 1] if 1 <= bride_nakshatra <= 27 else "Unknown",
            "pada": bride_pada,
            "gana": b_gana,
            "nadi": b_nadi,
            "yoni": b_yoni,
            "rashi_lord": b_lord,
        },
        "groom_summary": {
            "moon_sign": groom_moon_sign,
            "nakshatra_index": groom_nakshatra,
            "nakshatra_name": NAKSHATRA_NAMES[groom_nakshatra - 1] if 1 <= groom_nakshatra <= 27 else "Unknown",
            "pada": groom_pada,
            "gana": g_gana,
            "nadi": g_nadi,
            "yoni": g_yoni,
            "rashi_lord": g_lord,
        },
    }
