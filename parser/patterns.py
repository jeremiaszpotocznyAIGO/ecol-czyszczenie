# patterns.py
# Trzymamy tu TYLKO konfigurację: PARAM_PATTERNS, AUX, STATUS_RULES, status rank/typy.

from __future__ import annotations

# Kolumny używane przez model
FEATURE_COLS = [
    "Capacity",
    "Top_Up_Since_Last_Change",
    "Antimony",
    "Barium",
    "Color_ASTM",
    "Boron",
    "Chromium",
    "Tin",
    "Zinc",
    "Phosphorus",
    "Density_at_20C_1",
    "Density_at_20C_2",
    "Density_at_20C_3",
    "Aluminum",
    "Particles_greater_than_14um",
    "Particles_greater_than_21um",
    "Particles_greater_than_38um",
    "Particles_greater_than_4um",
    "Particles_greater_than_6um",
    "Particles_greater_than_70um",
    "Phenolic_inhibitor_FTIR",
    "Cleanliness_class_1",
    "Cleanliness_class_2",
    "Cleanliness_class_3",
    "Silicon",
    "Kinematic_viscosity_at_40C",
    "Demulsification_number",
    "Acid_number",
    "Base_number",
    "Lithium",
    "Magnesium",
    "Manganese",
    "Copper",
    "Molybdenum",
    "MPC_luminance",
    "MPC_value_a_red",
    "MPC_value_b_yellow",
    "MPC_index",
    "Breakdown_voltage",
    "Unclassified",
    "Nickel",
    "pH_value_at_20C",
    "Oxidation",
    "Lead",
    "Potassium",
    "PQ_index",
    "Alkaline_reserve",
    "Soot",
    "Sulfur",
    "Sodium",
    "Silver",
    "Sulfation",
    "Crystallization_temperature",
    "Flash_point_Cleveland",
    "Flash_point_closed_cup",
    "Titanium",
    "Vanadium",
    "Calcium",
    "Viscosity_index",
    "Nonmetallic_contaminants",
    "Glycol_content_IR_qualitative",
    "Glycol_content",
    "Solid_foreign_particles_content",
    "Water_content_IR",
    "Water_content_KF_method",
    "Water_content",
    "Adhesive_wear",
    "Abrasive_wear",
    "Fatigue_wear",
    "Iron",
    "Nitrites",
    "Overall_Assessment",
    "Diesel_fuel_content_qualitative",
    "Kinematic_viscosity_at_100C",
    "Fuel_content",
    "Dispersing_properties"]

# # Mapowanie nazwa angielskich do polskich
# FEATURE_DICT = {
#     "Capacity": "pojemność",
#     "Top_Up_Since_Last_Change": "dolewki_od_ostatniej_wymiany",
#     "Antimony": "antymon",
#     "Barium": "bar",
#     "Color_ASTM": "barwa_astm",
#     "Boron": "bor",
#     "Chromium": "chrom",
#     "Tin": "cyna",
#     "Zinc": "cynk",
#     "Phosphorus": "fosfor",
#     "Density_at_20C_1": "gęstość_w_20c_1",
#     "Density_at_20C_2": "gęstość_w_20c_2",
#     "Density_at_20C_3": "gęstość_w_20c_3",
#     "Aluminum": "glin",
#     "Particles_greater_than_14um": "cząstki_powyżej_14um",
#     "Particles_greater_than_21um": "cząstki_powyżej_21um",
#     "Particles_greater_than_38um": "cząstki_powyżej_38um",
#     "Particles_greater_than_4um": "cząstki_powyżej_4um",
#     "Particles_greater_than_6um": "cząstki_powyżej_6um",
#     "Particles_greater_than_70um": "cząstki_powyżej_70um",
#     "Phenolic_inhibitor_FTIR": "inhibitor_fenolowy_ftir",
#     "Cleanliness_class_1": "klasa_czystości_1",
#     "Cleanliness_class_2": "klasa_czystości_2",
#     "Cleanliness_class_3": "klasa_czystości_3",
#     "Silicon": "krzem",
#     "Kinematic_viscosity_at_40C": "lepkość_kinematyczna_w_40c",
#     "Demulsification_number": "liczba_demulgacji",
#     "Acid_number": "liczba_kwasowa",
#     "Base_number": "liczba_zasadowa",
#     "Lithium": "lit",
#     "Magnesium": "magnez",
#     "Manganese": "mangan",
#     "Copper": "miedź",
#     "Molybdenum": "molibden",
#     "MPC_luminance": "mpc_luminancja",
#     "MPC_value_a_red": "mpc_wartość_a_czerwony",
#     "MPC_value_b_yellow": "mpc_wartość_b_żółty",
#     "MPC_index": "mpc_indeks",
#     "Breakdown_voltage": "napięcie_przebicia",
#     "Unclassified": "nieklasyfikowane",
#     "Nickel": "nikiel",
#     "pH_value_at_20C": "ph_w_20c",
#     "Oxidation": "oksydacja",
#     "Lead": "ołów",
#     "Potassium": "potas",
#     "PQ_index": "pq_indeks",
#     "Alkaline_reserve": "rezerwa_alkaliczna",
#     "Soot": "sadza",
#     "Sulfur": "siarka",
#     "Sodium": "sód",
#     "Silver": "srebro",
#     "Sulfation": "sulfacja",
#     "Crystallization_temperature": "temperatura_krystalizacji",
#     "Flash_point_Cleveland": "temperatura_zapłonu_cleveland",
#     "Flash_point_closed_cup": "temperatura_zapłonu_tygiel_zamknięty",
#     "Titanium": "tytan",
#     "Vanadium": "wanad",
#     "Calcium": "wapń",
#     "Viscosity_index": "wskaźnik_lepkości",
#     "Nonmetallic_contaminants": "zanieczyszczenia_niemetaliczne",
#     "Glycol_content_IR_qualitative": "glikol_ir_jakościowo",
#     "Glycol_content": "zawartość_glikolu",
#     "Solid_foreign_particles_content": "zawartość_stałych_ciał_obcych",
#     "Water_content_IR": "zawartość_wody_ir",
#     "Water_content_KF_method": "zawartość_wody_metodą_kf",
#     "Water_content": "zawartość_wody",
#     "Adhesive_wear": "zużycie_adhezyjne",
#     "Abrasive_wear": "zużycie_abrazyjne",
#     "Fatigue_wear": "zużycie_zmęczeniowe",
#     "Iron": "żelazo",
#     "Nitrites": "azotyny",
#     "Overall_Assessment": "ocena_ogólna",
#     "Diesel_fuel_content_qualitative": "olej_napędowy_jakościowo",
#     "Kinematic_viscosity_at_100C": "lepkość_kinematyczna_w_100c",
#     "Fuel_content": "zawartość_paliwa",
#     "Dispersing_properties": "właściwości_dyspergujące",
# }


# PARAMETRY (wzorce)
PARAM_PATTERNS = {
    # olej / fizykochemia
    "lepkość": r"\blepko(ść|sci)\b|\breologicz\w*\b|\blepkości\b",
    "wskaźnik_lepkości": r"wskaźnik\s+lepkości|indeks\s+lepkości",
    "temperatura_zapłonu": r"(temperatur[a-y]\s+zapłonu|\bt\.\s*zapłonu\b|temp\.?\s*zapłonu)",
    "temperatura_krystalizacji": r"temperatur[a-y]\s+krystalizacji",
    "liczba_kwasowa": r"liczb[ay]\s+kwasow",
    "liczba_zasadowa": r"liczb[ay]\s+zasadow",
    "rezerwa_alkaliczna": r"rezerw[ay]\s+alkaliczn",
    "ph": r"\b(?:odczyn\s+)?p\s*h\b|\bodczyn\s+ph\b|\bi-?p\s*h\b",
    "pienienie": r"skłonno(ść|sci)\s+do\s+pienieni|pienieni[ae]",
    "oksydacja": r"oksydacj",
    "nitracja": r"nitracj",
    "sulfacja": r"sulfacj",
    "pozostałość_po_spopieleniu": r"pozostałość\s+po\s+spopieleniu",

    # zanieczyszczenia / czystość
    "woda": r"zawartość\s+wody|\bwod[ay]\b",
    "klasa_czystości": r"klas[ae]?\s+czystości|czystość\s+oleju|\bczystość\b",
    "stałe_ciała_obce": r"stał(e|ych)\s+ciał(a| obcych)|ciała\s+obce|zawartość\s+stałych\s+ciał\s+obcych|stałe\s+ciał[ao]\s+obcych|ciał\s+stałych",
    "zanieczyszczenia_stałe": r"(zanieczyszcze[nń]\w*\s+stał\w*|stał(e|ych)\s+zanieczyszcze[nń]\w*)",
    "własności_filtrujące": r"własno(ść|sci)\s+filtruj|membran",

    # paliwo / chłodziwo / IR
    "paliwo": r"(?:"
              r"poziom\s+paliw\w*"
              r"|zawartość\s+paliw\w*"
              r"|paliw\w*\s+jest"
              r"|paliw\w*\s+w\s+oleju"
              r"|obecno(ść|sci)\s+paliw\w*"
              r"|zanieczyszcz\w*\s+paliw\w*"
              r")",
    "olej_napędowy": r"oleju\s+napędowego|olej\s+napędowy|\bon\b|\bkomponentów?\s+on\b|\bkomponentów?\s+oleju\s+napędowego\b",
    "biokomponenty": r"biokomponent",
    "ft_ir": r"widm(?:ie|o)\s+ir|widm(?:ie|o)\s+w\s+podczerwieni|w\s+podczerwieni|ftir",
    "glikol": r"glikol",
    "płyn_chłodniczy": r"płyn(ów|em)?\s+chłodnicz|coolant|płynem?\s+chłodniczym|płynem?\s+chłodzącym",

    # metale / pierwiastki
    "sód": r"\bsod(u|em)?\b",
    "potas": r"\bpotas(u|em)?\b",
    "krzem": r"\bkrzem(u|em)?\b",
    "żelazo": r"\bżelaz(a|em)?\b",
    "miedź": r"\bmiedz(i|ią|y)?\b",
    "ołów": r"\bołow(iu|iem)?\b|\bołów\b",
    "glin": r"\bglin(u|em)?\b",
    "magnez": r"\bmagnez(u|em)?\b",
    "cynk": r"\bcynk(u|iem)?\b",
    "bor": r"\bbor(u|em)?\b",
    "chlor": r"\bchlor(u|em)?\b",
    "fosfor": r"\bfosfor(u|em)?\b",
    "cyna": r"\bcyn(a|y|ą|ie|i)\b",

    # indeks / cząstki / płyn
    "pq_indeks": r"\bpq\b|indeks\s*pq",
    "metale_zużyciowe": r"(?:"
        r"metalicznych\s+produkt(?:ów|y)\s+(?:zużycia|zuzycia)"
        r"|metali\s+(?:zużyciow(?:ych|e)?|zuzyciow(?:ych|e)?)"
        r"|pierwiastk(?:ów|i)\s+(?:zużyciow(?:ych|e)?|zuzyciow(?:ych|e)?)"
        r"|cząstek\s+(?:zużycia|zuzycia)"
        r"|cząstek\s+(?:zużyciow(?:ych|e)?|zuzyciow(?:ych|e)?)"
        r"|cząstki\s+(?:zużyciow(?:ych|e)?|zuzyciow(?:ych|e)?)"
        r"|cząstek\s+metalicznych"
    r")",
    "azotyny": r"azotyn(ów|y|u)?",
    "sadza": r"\bsadz[ay]\b",
    "iso_vg": r"\biso\s*vg\b",
    "dodatki_uszlachetniające": r"dodatk(?:ów|i)?\s+uszlachetniaj\w*|pakiet\s+dodatków",
}

# Mapowanie parametrów do kolumn
FEATURE_TO_PATTERN = {
    "Boron": "bor",
    "Tin": "cyna",
    "Zinc": "cynk",
    "Phosphorus": "fosfor",
    "Aluminum": "glin",
    "Silicon": "krzem",
    "Acid_number": "liczba_kwasowa",
    "Base_number": "liczba_zasadowa",
    "Magnesium": "magnez",
    "Copper": "miedź",
    "Lead": "ołów",
    "pH_value_at_20C": "ph",
    "Oxidation": "oksydacja",
    "Potassium": "potas",
    "PQ_index": "pq_indeks",
    "Alkaline_reserve": "rezerwa_alkaliczna",
    "Soot": "sadza",
    "Sodium": "sód",
    "Sulfation": "sulfacja",
    "Crystallization_temperature": "temperatura_krystalizacji",
    "Viscosity_index": "wskaźnik_lepkości",
    "Glycol_content_IR_qualitative": "glikol",
    "Glycol_content": "glikol",
    "Solid_foreign_particles_content": "stałe_ciała_obce",
    "Water_content_IR": "woda",
    "Water_content_KF_method": "woda",
    "Water_content": "woda",
    "Iron": "żelazo",
    "Nitrites": "azotyny",
    "Diesel_fuel_content_qualitative": "olej_napędowy",
    "Fuel_content": "paliwo",

    "Kinematic_viscosity_at_40C": "lepkość",
    "Kinematic_viscosity_at_100C": "lepkość",

    "Cleanliness_class_1": "klasa_czystości",
    "Cleanliness_class_2": "klasa_czystości",
    "Cleanliness_class_3": "klasa_czystości",

    "Flash_point_Cleveland": "temperatura_zapłonu",
    "Flash_point_closed_cup": "temperatura_zapłonu",
}

# Lista cech używanych przez model, które nie są wykrywane przez parser
NOT_COVERED = [
    "Capacity",
    "Top_Up_Since_Last_Change",
    "Antimony",
    "Barium",
    "Color_ASTM",
    "Chromium",
    "Density_at_20C_1",
    "Density_at_20C_2",
    "Density_at_20C_3",
    "Particles_greater_than_14um",
    "Particles_greater_than_21um",
    "Particles_greater_than_38um",
    "Particles_greater_than_4um",
    "Particles_greater_than_6um",
    "Particles_greater_than_70um",
    "Phenolic_inhibitor_FTIR",
    "Demulsification_number",
    "Lithium",
    "Manganese",
    "Molybdenum",
    "MPC_luminance",
    "MPC_value_a_red",
    "MPC_value_b_yellow",
    "MPC_index",
    "Breakdown_voltage",
    "Unclassified",
    "Nickel",
    "Sulfur",
    "Silver",
    "Titanium",
    "Vanadium",
    "Calcium",
    "Nonmetallic_contaminants",
    "Adhesive_wear",
    "Abrasive_wear",
    "Fatigue_wear",
    "Overall_Assessment",
    "Dispersing_properties",
]


# AUX (pomocnicze)
AUX = {
    "LIST_JOINERS": r"(?:\s*,\s*|\s+i\s+|\s+oraz\s+|\s+ani\s+)",
    "REPORT_VERBS": r"\b(zauważono|odnotowano|stwierdzono|nie\s+stwierdzono|nie\s+wykryto|wykryto|nie\s+określono|określono)\b",
    "MEASURE_LEADS": r"\b(poziom|zawartość|oznaczona|oznaczone|klasa|odczyn)\b",
    "NO_CORRELATION": r"\b(bez\s+korelacji\s+z|nie\s+wskazuje\s+na|nie\s+świadczy\s+o)\b",
    "NORMAL_PHRASES": r"\b(sytuacja\s+normalna|zjawisko\s+normalne|typow(a|e)\s+dla|jest\s+to\s+sytuacja\s+typowa)\b",
    "AVIATION_FUEL": r"\b(paliw\w*\s+lotnicz)\b|\bpochodzi\s+z\s+paliw\w*\b",

     "SECTION_CUT_HEADERS": r"\b(?:wnioski\s+i\s+zalecenia|zalecenia\s+i\s+wnioski)\b",
}

# STATUSY (kolejność = priorytet)
STATUS_RULES = [
    ("nieoznaczono",
        r"(?:"
        r"(?:niemożliw\w*|nie było możliwe|brak możliwości)\s+(?:oznaczen\w*|oznaczeni\w*|pomiar\w*|wykonan\w*|określen\w*)"
        r"|z\s+powodu\s+zbyt\s+małej\s+ilości.*?(?:oznaczen\w*|oznaczeni\w*|pomiar\w*|określen\w*)\s+(?:było\s+niemożliw\w*|nie\s+było\s+możliwe)"
        r"|nie\s+przedstawion\w*\s+wynik\w*"
        r"|niemożliw\w*\s+jest\s+określen\w*"
        r")"),
    ("brak_wykrycia", r"nie stwierdzono|nie wykryto|brak obecnoś|nie wykazano"),

    ("mocno_podwyższony", r"\bmocno\b.*\b(podwyższ|podnies)\w*"),
    ("mocno_obniżony",   r"\bmocno\b.*\bobniż\w*"),

    ("powyżej_dopuszczalnego_limitu", r"powyżej\s+dopuszczalnego\s+limit[u]?"),
    ("poza_dopuszczalnym_zakresem",
        r"poza\s+(dopuszczalnym|akceptowalnym)\s+zakres(em|ie)"
        r"|nie\s+spełnia\s+wymagań"
        r"|wymaga\s+poprawy"),
    ("krytycznie_podniesiony", r"krytyczn(ie|y|a).*(podnies|podwyższ|wysok)"),
    ("krytycznie_obniżony", r"krytyczn(ie|y|a).*(obniż|niski)"),

    ("nieznacznie_podniesiony", r"\bnieznaczn(ie|y|a)\b.*\b(podnies|podwyższ)\w*"),
    ("nieznacznie_obniżony",   r"\bnieznaczn(ie|y|a)\b.*\bobniż\w*"),

    # "wzrósł jedynie nieznacznie" jako sygnał lekkiego wzrostu
    # ("nieznacznie_podniesiony", r"(?:jedynie\s+)?nieznaczn\w*\s+wzrósł|wzrósł\s+(?:jedynie\s+)?nieznaczn\w*"),

    # # ogólny trend/wzrost (bardzo słaby sygnał → często tylko pomocniczy)
    # ("podniesiony", r"wzrostow\w*|wzrast\w*|wzrósł|wzrosł\w*|rosnąc\w*|przyrost\w*"),

    ("znacznie_podniesiony", r"\b(znacznie|wyraźnie|istotnie)\b.*\b(podnies|podwyższ)\w*"),
    ("znacznie_obniżony",    r"\b(znacznie|wyraźnie|istotnie)\b.*\bobniż\w*"),
    ("mocno_pogorszony",     r"(mocno|silnie|znacznie)\s+pogorsz"),

    ("lekko_podniesiony", r"\blekko\b.*\b(podnies|podwyższ)\w*"),
    ("lekko_obniżony",    r"\blekko\b.*\bobniż\w*"),

    ("pogorszony", r"pogorsz(on|one|ona|ony)|pogorszon[aeoy]"),
    ("nietypowy",   r"nietypow"),

    ("w_zakresie_granicznym",   r"w\s+zakresie\s+granicznym|zakresie\s+granicznym|na\s+poziomie\s+granicznym|poniżej\s+dolnego\s+zakresu\s+granicznego"),
    ("w_zakresie_bezpiecznym",  r"w\s+bezpiecznym\s+(zakresie|przedziale)|na\s+bezpiecznym\s+poziomie|bezpiecznym\s+poziomie"),
    ("w_akceptowalnym_zakresie", r"w\s+akceptowalnym\s+(zakresie|przedziale)|na\s+akceptowalnym\s+poziomie|akceptowaln(ym|y|a)"),
    ("w_dopuszczalnym_zakresie", r"w\s+dopuszczalnym\s+(zakresie|przedziale)|na\s+poziomie\s+dopuszczalnym|dopuszczaln(ym|y|a)"),
    ("w_normie",               r"\bw\s+normie\b|w\s+granicach\s+normy|na\s+poziomie\s+normy"),

    ("w_zakresie_typowym", r"mieści\s+się\s+w\s+zakresie\s+typowym|w\s+zakresie\s+typowym|na\s+poziomie\s+typowym|wskazuje\s+na\s+olej\s+klasy|na\s+poziomie\s+oczekiwanym(?:\s+dla)?"),

    ("poniżej_typowego", r"poniżej\s+zakresu\s+typowego|poniżej\s+klasy\s+sae|poniżej\s+zakresu\s+dopuszczalnego|poniżej\s+dopuszczalnego\s+zakresu|poniżej\s+wartości\s+katalogowych|poniżej\s+oczekiwanej|bliska\s+dolnej\s+granicy\s+zakresu\s+typowego"),
    ("powyżej_typowego", r"powyżej\s+zakresu\s+dopuszczalnego|powyżej\s+wartości\s+oczekiwanej|powyżej\s+typowego"),
    ("nieznacznie_odbiega", r"odbiega.*nieznaczn|nieznacznie.*odbiega|jedynie\s+nieznacznie\s+odbiega"),

    ("podniesiony", r"podniesion|podwyższon|\bwysok(i|a|ie)\s+poziom\b|\bwysoka\s+zawartość\b"),
    ("obniżony", r"obniżon|\bniski\s+poziom\b|na\s+niskim\s+poziomie|poniżej\s+poziomu\s+dopuszczalnego|poniżej\s+wymagań"),
    

    ("wysoki", r"na\s+wysokim\s+poziomie|wysoki\s+poziom"),
    ("odbiega_od_referencji", r"odchylen\w*\s+od\s+próbki\s+referencyjnej|odbiega\s+od\s+próbki\s+referencyjnej|wykazuje\s+odchylenia"),
]

# Słownik porządkujący statusy na osi "odchyłu"
STATUS_TO_ABNORMALITY = {
    # brak wiarygodnego wyniku
    "nieoznaczono": None,

    # brak wykrycia / norma
    "brak_wykrycia": 0.0,
    "w_normie": 0.0,
    "w_zakresie_typowym": 0.0,
    "w_zakresie_bezpiecznym": 0.0,
    "w_akceptowalnym_zakresie": 0.0,
    "w_dopuszczalnym_zakresie": 0.0,

    # graniczne / bardzo lekkie odchylenie
    "w_zakresie_granicznym": 0.25,
    "nieznacznie_odbiega": 0.25,

    # lekkie / małe odchylenie
    "nieznacznie_podniesiony": 0.5,
    "nieznacznie_obniżony": 0.5,
    "lekko_podniesiony": 0.5,
    "lekko_obniżony": 0.5,
    "podniesiony": 0.5,
    "obniżony": 0.5,
    "powyżej_typowego": 0.5,
    "poniżej_typowego": 0.5,
    "nietypowy": 0.5,
    "pogorszony": 0.5,
    "wysoki": 0.5,

    # wyraźne odchylenie
    "znacznie_podniesiony": 0.75,
    "znacznie_obniżony": 0.75,
    "mocno_podwyższony": 0.75,
    "mocno_obniżony": 0.75,
    "mocno_pogorszony": 0.75,
    "poza_dopuszczalnym_zakresem": 0.75,
    "powyżej_dopuszczalnego_limitu": 0.75,

    # krytyczne
    "krytycznie_podniesiony": 1.0,
    "krytycznie_obniżony": 1.0,
}


# WHITELISTY / GLOBALNE
NEGATION_WHITELIST = {
    "glikol", "paliwo", "olej_napędowy", "płyn_chłodniczy",
    "oksydacja", "nitracja", "sulfacja", "sadza",
}

# Ranking statusów
STATUS_KIND = {
    "mocno_podwyższony": "magnitude",
    "mocno_obniżony": "magnitude",
    "krytycznie_podniesiony": "magnitude",
    "krytycznie_obniżony": "magnitude",
    "znacznie_podniesiony": "magnitude",
    "znacznie_obniżony": "magnitude",
    "nieznacznie_podniesiony": "magnitude",
    "nieznacznie_obniżony": "magnitude",
    "lekko_podniesiony": "magnitude",
    "lekko_obniżony": "magnitude",
    "podniesiony": "magnitude",
    "obniżony": "magnitude",
    "powyżej_dopuszczalnego_limitu": "magnitude",
    "poza_dopuszczalnym_zakresem": "magnitude",
    "poniżej_typowego": "magnitude",
    "powyżej_typowego": "magnitude",

    "w_normie": "range",
    "w_zakresie_bezpiecznym": "range",
    "w_akceptowalnym_zakresie": "range",
    "w_dopuszczalnym_zakresie": "range",
    "w_zakresie_granicznym": "range",
    "w_zakresie_typowym": "range",

    "pogorszony": "other",
    "mocno_pogorszony": "other",
    "nietypowy": "other",
    "brak_wykrycia": "other",
    "nieoznaczono": "other",
    "nieznacznie_odbiega": "other",
    "wysoki": "other",
}

STATUS_SCORE = {
    "nieoznaczono": 0,
    "brak_wykrycia": 5,

    "w_zakresie_typowym": 20,
    "w_normie": 25,
    "w_zakresie_bezpiecznym": 24,
    "w_akceptowalnym_zakresie": 23,
    "w_dopuszczalnym_zakresie": 22,
    "w_zakresie_granicznym": 21,

    "nieznacznie_odbiega": 30,
    "pogorszony": 32,
    "mocno_pogorszony": 35,
    "nietypowy": 36,
    "wysoki": 33,

    "lekko_podniesiony": 40,
    "lekko_obniżony": 40,
    "nieznacznie_podniesiony": 41,
    "nieznacznie_obniżony": 41,

    "podniesiony": 50,
    "obniżony": 50,

    "znacznie_podniesiony": 70,
    "znacznie_obniżony": 70,
    "mocno_podwyższony": 75,
    "mocno_obniżony": 75,

    "poniżej_typowego": 80,
    "powyżej_typowego": 80,

    "krytycznie_podniesiony": 90,
    "krytycznie_obniżony": 90,
    "powyżej_dopuszczalnego_limitu": 95,
    "poza_dopuszczalnym_zakresem": 96,
}



#### TRENDS

TREND_WORD = r"\btrend\w*\b"

TREND_STATUS_RULES = [
    # brak możliwości oceny trendu
    (
        "nieoznaczono",
        r"(?:"
        r"brak\s+(?:wartości|wyników)\s+historycznych\s+uniemożliwia(?:\s+jednak)?\s+ocenę\s+trend\w*"
        r"|uniemożliwia(?:\s+jednak)?\s+ocenę\s+trend\w*"
        r")",
    ),

    # stabilny / norma / bez zmian
    (
        "w_normie",
        r"(?:"
        r"trend\w*(?:\s+[\wąćęłńóśźż]+\s+i\s+[\wąćęłńóśźż]+)?\s+(?:jednak\s+)?(?:jest\s+)?stabiln\w*"
        r"|stabiln\w*\s+trend\w*"
        r"|trend\w*\s+(?:jest\s+)?w\s+normie"
        r"|trend\w*\s+(?:mieści\s+się\s+)?w\s+granicach\s+normy"
        r"|trend\w*\s+w\s+(?:zakresie|przedziale)\s+(?:typowym|bezpiecznym|akceptowalnym|dopuszczalnym)"
        r"|w\s+trendzie\s+stał\w*"
        r"|trend\w*\s+stał\w*"
        r"|trend\w*\s+utrzymuje\s+się\s+na\s+tym\s+samym\s+poziomie"
        r"|utrzymuje\s+się\s+na\s+tym\s+samym\s+poziomie"
        r"|na\s+tym\s+samym\s+poziomie\s+jak\s+w\s+badaniu\s+poprzednim"
        r"|przebieg\s+trend\w*.*?stabiln\w*"
        r")",
    ),

    # trend wzrostowy — wskazówka
    (
        "wzrostowy",
        r"(?:"
        r"trend\w*\s+(?:jest\s+)?(?:jednak\s+)?(?:wyraźnie\s+)?(?:wzrostow\w*|wzrosto\w*|rosnąc\w*)"
        r"|(?:wzrostow\w*|wzrosto\w*|rosnąc\w*)\s+trend\w*"
        r"|w\s+trendzie\s+(?:wzrostow\w*|rosnąc\w*)"
        r"|charakterystyce\s+trend\w*\s+poziom\s+(?:wzrostow\w*|wzrosto\w*)"
        r"|na\s+charakterystyce\s+trend\w*\s+poziom\s+(?:wzrostow\w*|wzrosto\w*)"
        r"|charakterystyce\s+trend\w*\s+widoczn\w*\s+stabiln\w*\s+wzrost"
        r"|na\s+charakterystyce\s+trend\w*\s+widoczn\w*\s+stabiln\w*\s+wzrost"
        r"|trend\w*.*?widoczn\w*\s+wzrost"
        r"|w\s+badaniu\s+trend\w*\s+widoczn\w*\s+wzrost"
        r"|(?:zawartość|poziom|wartość)?\s*.*?(?:wzrosł\w*|wzrósł\w*)\s+od\s+poprzedni\w*\s+(?:badani\w*|analiz\w*)"
        r"|(?:zawartość|poziom|wartość)?\s*.*?(?:wzros\w*|wzrós\w*)\s+od\s+poprzedni\w*\s+(?:badani\w*|analiz\w*)"
        r"|(?:zachowan\w*\s+)?dynamik\w*\s+przyrost\w*"
        r"|przyrost\w+\s+(?:zawartości\s+|poziomu\s+|wartości\s+)?"
        r")",
    ),

    # trend spadkowy — wskazówka
    (
        "spadkowy",
        r"(?:"
        r"trend\w*\s+(?:jest\s+)?(?:jednak\s+)?(?:wyraźnie\s+)?(?:spadkow\w*|malejąc\w*|opadając\w*)"
        r"|(?:spadkow\w*|malejąc\w*|opadając\w*)\s+trend\w*"
        r"|w\s+trendzie\s+(?:malejąc\w*|spadkow\w*|opadając\w*)"
        r"|charakterystyce\s+trend\w*\s+poziom\s+(?:spadkow\w*|malejąc\w*|opadając\w*)"
        r"|na\s+charakterystyce\s+trend\w*\s+poziom\s+(?:spadkow\w*|malejąc\w*|opadając\w*)"
        r"|charakterystyce\s+trend\w*\s+widoczn\w*\s+stabiln\w*\s+spadek"
        r"|na\s+charakterystyce\s+trend\w*\s+widoczn\w*\s+stabiln\w*\s+spadek"
        r"|trend\w*.*?widoczn\w*\s+spadek"
        r"|w\s+badaniu\s+trend\w*\s+widoczn\w*\s+spadek"
        r")",
    ),

    # trend do obserwacji — nie jest normalny, ale bez jasnego kierunku
    (
        "do_obserwacji",
        r"(?:"
        r"obserwacj\w*\s+trend\w*"
        r"|obserwować\s+trend\w*"
        r"|obserwować\s+zmian\w*\s+trend\w*"
        r"|zmian\w*\s+trend\w*"
        r"|trend\w*\s+zmian"
        r"|obserwację\s+trend\w*\s+zmian"
        r")",
    ),
]