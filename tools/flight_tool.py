import os
import certifi
import re
import requests
import airportsdata
import pycountry
from dotenv import load_dotenv

load_dotenv()

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Default departure airport used only when the user gives a destination
# but does not specify where they are flying from.
# IMPORTANT: This must be a real 3-letter IATA airport code, e.g. DEL or IXC.
# Set DEFAULT_ORIGIN_IATA=IXC in your .env if Chandigarh is your default origin.
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "DEL").strip().upper()

BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load('IATA')

COUNTRY_ALIASES = {

    # United States
    "usa": "USA",
    "u.s.a": "USA",
    "u.s.a.": "USA",
    "u.s.": "USA",
    "us": "USA",
    "u.s": "USA",
    "united states": "USA",
    "united states of america": "USA",
    "america": "USA",

    # United Kingdom
    "uk": "GBR",
    "u.k": "GBR",
    "u.k.": "GBR",
    "united kingdom": "GBR",
    "great britain": "GBR",
    "britain": "GBR",
    "british": "GBR",

    # India
    "india": "IND",
    "bharat": "IND",
    "hindustan": "IND",
    "republic of india": "IND",
    "in": "IND",

    # Canada
    "canada": "CAN",
    "ca": "CAN",
    "can": "CAN",

    # Australia
    "australia": "AUS",
    "aus": "AUS",
    "commonwealth of australia": "AUS",

    # United Arab Emirates
    "uae": "ARE",
    "u.a.e": "ARE",
    "u.a.e.": "ARE",
    "united arab emirates": "ARE",
    "emirates": "ARE",

    # Saudi Arabia
    "saudi arabia": "SAU",
    "ksa": "SAU",
    "k.s.a": "SAU",
    "kingdom of saudi arabia": "SAU",

    # New Zealand
    "new zealand": "NZL",
    "nz": "NZL",
    "n.z": "NZL",
    "nzl": "NZL",

    # Singapore
    "singapore": "SGP",
    "sg": "SGP",
    "sgp": "SGP",
    "republic of singapore": "SGP",

    # Germany
    "germany": "DEU",
    "de": "DEU",
    "deu": "DEU",
    "deutschland": "DEU",
    "federal republic of germany": "DEU",

    # France
    "france": "FRA",
    "fr": "FRA",
    "fra": "FRA",
    "french republic": "FRA",

    # Italy
    "italy": "ITA",
    "it": "ITA",
    "ita": "ITA",
    "italia": "ITA",

    # Spain
    "spain": "ESP",
    "es": "ESP",
    "esp": "ESP",
    "espana": "ESP",
    "españa": "ESP",

    # Japan
    "japan": "JPN",
    "jp": "JPN",
    "jpn": "JPN",
    "nippon": "JPN",
    "nihon": "JPN",

    # China
    "china": "CHN",
    "cn": "CHN",
    "chn": "CHN",
    "prc": "CHN",
    "p.r.c": "CHN",
    "people's republic of china": "CHN",
    "peoples republic of china": "CHN",

    # South Korea
    "south korea": "KOR",
    "korea": "KOR",
    "kr": "KOR",
    "kor": "KOR",
    "republic of korea": "KOR",

    # Russia
    "russia": "RUS",
    "ru": "RUS",
    "rus": "RUS",
    "russian federation": "RUS",

    # Brazil
    "brazil": "BRA",
    "br": "BRA",
    "bra": "BRA",
    "brasil": "BRA",

    # Mexico
    "mexico": "MEX",
    "mx": "MEX",
    "mex": "MEX",
    "united mexican states": "MEX",

    # Netherlands
    "netherlands": "NLD",
    "holland": "NLD",
    "nl": "NLD",
    "nld": "NLD",

    # Switzerland
    "switzerland": "CHE",
    "ch": "CHE",
    "che": "CHE",
    "swiss confederation": "CHE",

    # Ireland
    "ireland": "IRL",
    "ie": "IRL",
    "irl": "IRL",
    "republic of ireland": "IRL",

    # South Africa
    "south africa": "ZAF",
    "za": "ZAF",
    "zaf": "ZAF",
    "rsa": "ZAF",
    "republic of south africa": "ZAF",

    # Thailand
    "thailand": "THA",
    "th": "THA",
    "tha": "THA",
    "kingdom of thailand": "THA",

    # Malaysia
    "malaysia": "MYS",
    "my": "MYS",
    "mys": "MYS",

    # Indonesia
    "indonesia": "IDN",
    "id": "IDN",
    "idn": "IDN",

    # Turkey / Türkiye
    "turkey": "TUR",
    "türkiye": "TUR",
    "turkiye": "TUR",
    "tr": "TUR",
    "tur": "TUR",

    # Egypt
    "egypt": "EGY",
    "eg": "EGY",
    "egy": "EGY",
    "arab republic of egypt": "EGY",

    # Pakistan
    "pakistan": "PAK",
    "pk": "PAK",
    "pak": "PAK",
    "islamic republic of pakistan": "PAK",

    # Bangladesh
    "bangladesh": "BGD",
    "bd": "BGD",
    "bgd": "BGD",

    # Sri Lanka
    "sri lanka": "LKA",
    "ceylon": "LKA",
    "lk": "LKA",
    "lka": "LKA",

    # Nepal
    "nepal": "NPL",
    "np": "NPL",
    "npl": "NPL",

    # Qatar
    "qatar": "QAT",
    "qa": "QAT",
    "qat": "QAT",

    # Kuwait
    "kuwait": "KWT",
    "kw": "KWT",
    "kwt": "KWT",

    # Oman
    "oman": "OMN",
    "om": "OMN",
    "omn": "OMN",

    # Bahrain
    "bahrain": "BHR",
    "bh": "BHR",
    "bhr": "BHR",

    # Vietnam
    "vietnam": "VNM",
    "viet nam": "VNM",
    "vn": "VNM",
    "vnm": "VNM",

    # Philippines
    "philippines": "PHL",
    "ph": "PHL",
    "phl": "PHL",

    # Sweden
    "sweden": "SWE",
    "se": "SWE",
    "swe": "SWE",

    # Norway
    "norway": "NOR",
    "no": "NOR",
    "nor": "NOR",

    # Denmark
    "denmark": "DNK",
    "dk": "DNK",
    "dnk": "DNK",

    # Finland
    "finland": "FIN",
    "fi": "FIN",
    "fin": "FIN",

    # Portugal
    "portugal": "PRT",
    "pt": "PRT",
    "prt": "PRT",

    # Greece
    "greece": "GRC",
    "gr": "GRC",
    "grc": "GRC",
    "hellas": "GRC",

    # Poland
    "poland": "POL",
    "pl": "POL",
    "pol": "POL",

    # Austria
    "austria": "AUT",
    "at": "AUT",
    "aut": "AUT",

    # Belgium
    "belgium": "BEL",
    "be": "BEL",
    "bel": "BEL",

    # Czech Republic
    "czech republic": "CZE",
    "czechia": "CZE",
    "cz": "CZE",
    "cze": "CZE",

    # Argentina
    "argentina": "ARG",
    "ar": "ARG",
    "arg": "ARG",

    # Chile
    "chile": "CHL",
    "cl": "CHL",
    "chl": "CHL",

    # Colombia
    "colombia": "COL",
    "co": "COL",
    "col": "COL",

    # Nigeria
    "nigeria": "NGA",
    "ng": "NGA",
    "nga": "NGA",

    # Kenya
    "kenya": "KEN",
    "ke": "KEN",
    "ken": "KEN",

    # Morocco
    "morocco": "MAR",
    "ma": "MAR",
    "mar": "MAR",

    # Israel
    "israel": "ISR",
    "il": "ISR",
    "isr": "ISR",

    # Ukraine
    "ukraine": "UKR",
    "ua": "UKR",
    "ukr": "UKR",

    # Iceland
    "iceland": "ISL",
    "is": "ISL",
    "isl": "ISL",
}

# Preferred main airport for country-level search
COUNTRY_MAIN_AIRPORT = {
  "AF": "KBL", "AFG": "KBL",
  "AL": "TIA", "ALB": "TIA",
  "DZ": "ALG", "DZA": "ALG",
  "AD": "LEU", "AND": "LEU",
  "AO": "LAD", "AGO": "LAD",
  "AG": "ANU", "ATG": "ANU",
  "AR": "EZE", "ARG": "EZE",
  "AM": "EVN", "ARM": "EVN",
  "AU": "SYD", "AUS": "SYD",
  "AT": "VIE", "AUT": "VIE",
  "AZ": "GYD", "AZE": "GYD",
  "BS": "NAS", "BHS": "NAS",
  "BH": "BAH", "BHR": "BAH",
  "BD": "DAC", "BGD": "DAC",
  "BB": "BGI", "BRB": "BGI",
  "BY": "MSQ", "BLR": "MSQ",
  "BE": "BRU", "BEL": "BRU",
  "BZ": "BZE", "BLZ": "BZE",
  "BJ": "COO", "BEN": "COO",
  "BT": "PBH", "BTN": "PBH",
  "BO": "LPB", "BOL": "LPB",
  "BA": "SJJ", "BIH": "SJJ",
  "BW": "GBE", "BWA": "GBE",
  "BR": "GRU", "BRA": "GRU",
  "BN": "BWN", "BRN": "BWN",
  "BG": "SOF", "BGR": "SOF",
  "BF": "OUA", "BFA": "OUA",
  "BI": "BJM", "BDI": "BJM",
  "KH": "PNH", "KHM": "PNH",
  "CM": "DLA", "CMR": "DLA",
  "CA": "YYZ", "CAN": "YYZ",
  "CV": "RAI", "CPV": "RAI",
  "CF": "BGF", "CAF": "BGF",
  "TD": "NDJ", "TCD": "NDJ",
  "CL": "SCL", "CHL": "SCL",
  "CN": "PEK", "CHN": "PEK",
  "CO": "BOG", "COL": "BOG",
  "KM": "HAH", "COM": "HAH",
  "CG": "BZV", "COG": "BZV",
  "CD": "FIH", "COD": "FIH",
  "CR": "SJO", "CRI": "SJO",
  "CI": "ABJ", "CIV": "ABJ",
  "HR": "ZAG", "HRV": "ZAG",
  "CU": "HAV", "CUB": "HAV",
  "CY": "LCA", "CYP": "LCA",
  "CZ": "PRG", "CZE": "PRG",
  "DK": "CPH", "DNK": "CPH",
  "DJ": "JIB", "DJI": "JIB",
  "DM": "DOM", "DMA": "DOM",
  "DO": "SDQ", "DOM": "SDQ",
  "EC": "UIO", "ECU": "UIO",
  "EG": "CAI", "EGY": "CAI",
  "SV": "SAL", "SLV": "SAL",
  "GQ": "SSG", "GNQ": "SSG",
  "ER": "ASM", "ERI": "ASM",
  "EE": "TLL", "EST": "TLL",
  "SZ": "SHO", "SWZ": "SHO",
  "ET": "ADD", "ETH": "ADD",
  "FJ": "NAN", "FJI": "NAN",
  "FI": "HEL", "FIN": "HEL",
  "FR": "CDG", "FRA": "CDG",
  "GA": "LBV", "GAB": "LBV",
  "GM": "BJL", "GMB": "BJL",
  "GE": "TBS", "GEO": "TBS",
  "DE": "FRA", "DEU": "FRA",
  "GH": "ACC", "GHA": "ACC",
  "GR": "ATH", "GRC": "ATH",
  "GD": "GND", "GRD": "GND",
  "GT": "GUA", "GTM": "GUA",
  "GN": "CKY", "GIN": "CKY",
  "GW": "OXB", "GNB": "OXB",
  "GY": "GEO", "GUY": "GEO",
  "HT": "PAP", "HTI": "PAP",
  "HN": "SAP", "HND": "SAP",
  "HU": "BUD", "HUN": "BUD",
  "IS": "KEF", "ISL": "KEF",
  "IN": "DEL", "IND": "DEL",
  "ID": "CGK", "IDN": "CGK",
  "IR": "IKA", "IRN": "IKA",
  "IQ": "BGW", "IRQ": "BGW",
  "IE": "DUB", "IRL": "DUB",
  "IL": "TLV", "ISR": "TLV",
  "IT": "FCO", "ITA": "FCO",
  "JM": "KIN", "JAM": "KIN",
  "JP": "HND", "JPN": "HND",
  "JO": "AMM", "JOR": "AMM",
  "KZ": "ALA", "KAZ": "ALA",
  "KE": "NBO", "KEN": "NBO",
  "KI": "TRW", "KIR": "TRW",
  "KP": "FNJ", "PRK": "FNJ",
  "KR": "ICN", "KOR": "ICN",
  "KW": "KWI", "KWT": "KWI",
  "KG": "FRU", "KGZ": "FRU",
  "LA": "VTE", "LAO": "VTE",
  "LV": "RIX", "LVA": "RIX",
  "LB": "BEY", "LBN": "BEY",
  "LS": "MSU", "LSO": "MSU",
  "LR": "ROB", "LBR": "ROB",
  "LY": "MJI", "LBY": "MJI",
  "LI": "ACH", "LIE": "ACH",
  "LT": "VNO", "LTU": "VNO",
  "LU": "LUX", "LUX": "LUX",
  "MG": "TNR", "MDG": "TNR",
  "MW": "LLW", "MWI": "LLW",
  "MY": "KUL", "MYS": "KUL",
  "MV": "MLE", "MDV": "MLE",
  "ML": "BKO", "MLI": "BKO",
  "MT": "MLA", "MLT": "MLA",
  "MH": "MAJ", "MHL": "MAJ",
  "MR": "NKC", "MRT": "NKC",
  "MU": "MRU", "MUS": "MRU",
  "MX": "MEX", "MEX": "MEX",
  "FM": "PNI", "FSM": "PNI",
  "MD": "RMO", "MDA": "RMO",
  "MC": "NCE", "MCO": "NCE",
  "MN": "UBN", "MNG": "UBN",
  "ME": "TGD", "MNE": "TGD",
  "MA": "CMN", "MAR": "CMN",
  "MZ": "MPM", "MOZ": "MPM",
  "MM": "RGN", "MMR": "RGN",
  "NA": "WDH", "NAM": "WDH",
  "NR": "INU", "NRU": "INU",
  "NP": "KTM", "NPL": "KTM",
  "NL": "AMS", "NLD": "AMS",
  "NZ": "AKL", "NZL": "AKL",
  "NI": "MGA", "NIC": "MGA",
  "NE": "NIM", "NER": "NIM",
  "NG": "LOS", "NGA": "LOS",
  "MK": "SKP", "MKD": "SKP",
  "NO": "OSL", "NOR": "OSL",
  "OM": "MCT", "OMN": "MCT",
  "PK": "KHI", "PAK": "KHI",
  "PW": "ROR", "PLW": "ROR",
  "PS": "GZA", "PSE": "GZA",
  "PA": "PTY", "PAN": "PTY",
  "PG": "POM", "PNG": "POM",
  "PY": "ASU", "PRY": "ASU",
  "PE": "LIM", "PER": "LIM",
  "PH": "MNL", "PHL": "MNL",
  "PL": "WAW", "POL": "WAW",
  "PT": "LIS", "PRT": "LIS",
  "QA": "DOH", "QAT": "DOH",
  "RO": "OTP", "ROU": "OTP",
  "RU": "SVO", "RUS": "SVO",
  "RW": "KGL", "RWA": "KGL",
  "KN": "SKB", "KNA": "SKB",
  "LC": "UVF", "LCA": "UVF",
  "VC": "SVD", "VCT": "SVD",
  "WS": "APW", "WSM": "APW",
  "SM": "CIA", "SMR": "CIA",
  "ST": "TMS", "STP": "TMS",
  "SA": "RUH", "SAU": "RUH",
  "SN": "DSS", "SEN": "DSS",
  "RS": "BEG", "SRB": "BEG",
  "SC": "SEZ", "SYC": "SEZ",
  "SL": "FNA", "SLE": "FNA",
  "SK": "BTS", "SVK": "BTS",
  "SI": "LJU", "SVN": "LJU",
  "SB": "HIR", "SLB": "HIR",
  "SO": "MGQ", "SOM": "MGQ",
  "ZA": "JNB", "ZAF": "JNB",
  "SS": "JUB", "SSD": "JUB",
  "ES": "MAD", "ESP": "MAD",
  "LK": "CMB", "LKA": "CMB",
  "SD": "PZU", "SDN": "PZU",
  "SR": "PBM", "SUR": "PBM",
  "SE": "ARN", "SWE": "ARN",
  "CH": "ZRH", "CHE": "ZRH",
  "SY": "DAM", "SYR": "DAM",
  "TW": "TPE", "TWN": "TPE",
  "TJ": "DYU", "TJK": "DYU",
  "TZ": "DAR", "TZA": "DAR",
  "TH": "BKK", "THA": "BKK",
  "TL": "DIL", "TLS": "DIL",
  "TG": "LFW", "TGO": "LFW",
  "TO": "TBU", "TON": "TBU",
  "TT": "POS", "TTO": "POS",
  "TN": "TUN", "TUN": "TUN",
  "TR": "IST", "TUR": "IST",
  "TM": "ASB", "TKM": "ASB",
  "TV": "FUN", "TUV": "FUN",
  "UG": "EBB", "UGA": "EBB",
  "UA": "KBP", "UKR": "KBP",
  "AE": "DXB", "ARE": "DXB",
  "GB": "LHR", "GBR": "LHR",
  "US": "JFK", "USA": "JFK",
  "UY": "MVD", "URY": "MVD",
  "UZ": "TAS", "UZB": "TAS",
  "VU": "VLI", "VUT": "VLI",
  "VA": "FCO", "VAT": "FCO",
  "VE": "CCS", "VEN": "CCS",
  "VN": "SGN", "VNM": "SGN",
  "YE": "SAH", "YEM": "SAH",
  "ZM": "LUN", "ZMB": "LUN",
  "ZW": "HRE", "ZWE": "HRE"
}

CITY_MAIN_AIRPORT = {
    "Dhaka": "DAC",
    "Delhi": "DEL",
    "Mumbai": "BOM",
    "Bengaluru": "BLR",
    "Chennai": "MAA",
    "Kolkata": "CCU",
    "Hyderabad": "HYD",
    "Pune": "PNQ",
    "Ahmedabad": "AMD",
    "Jaipur": "JAI",
    "Chandigarh": "IXC",
    "Amritsar": "ATQ",
    "Goa": "GOI",
    "London": "LHR",
    "New York": "JFK",
    "Paris": "CDG",
    "Dubai": "DXB",
    "Singapore": "SIN",
    "Bangkok": "BKK",
    "Tokyo": "HND",
    "Sydney": "SYD",
    "Toronto": "YYZ",
    "San Francisco": "SFO",
    "Los Angeles": "LAX",
    "Frankfurt": "FRA",
    "Amsterdam": "AMS",
    "Rome": "FCO"
}

def clean_text(text: str) -> str:
    """Normalize user-entered text before looking it up.

    Example: "  New Delhi Trip! " -> "new delhi"
    """
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)  # Remove punctuation.
    text = re.sub(r"\s+", " ", text)          # Collapse repeated spaces.

    # These words describe the request, not a geographic location.
    stop_words = {
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "information",
        "hotels", "sightseeing", "under", "budget", "info",
    }
    words = [word for word in text.split() if word not in stop_words]
    return " ".join(words).strip()


def normalize_country_code(country_code: str):
    """Convert either ISO alpha-2 or alpha-3 country code to ISO alpha-2.

    COUNTRY_ALIASES contains a mixture of alpha-3 values (e.g. IND), while
    pycountry and many airport datasets use alpha-2 (e.g. IN). Normalize at
    the boundary so country comparisons are consistent.
    """
    if not country_code:
        return None

    code = country_code.strip().upper()
    try:
        if len(code) == 2:
            country = pycountry.countries.get(alpha_2=code)
        elif len(code) == 3:
            country = pycountry.countries.get(alpha_3=code)
        else:
            country = None
        return country.alpha_2 if country else None
    except (AttributeError, LookupError):
        return None


def country_name_to_code(text: str):
    """Resolve a country name/alias to one consistent ISO alpha-2 code."""
    normalized = clean_text(text)
    if not normalized:
        return None

    # First try the explicit aliases (e.g. USA, Bharat, UAE).
    alias_code = COUNTRY_ALIASES.get(normalized)
    if alias_code:
        return normalize_country_code(alias_code)

    # pycountry handles standard country names and many official variants.
    try:
        country = pycountry.countries.lookup(normalized)
        return country.alpha_2
    except LookupError:
        pass

    # If a country name appears inside a longer phrase, find it by word
    # boundaries so that a short name does not match part of another word.
    for country in pycountry.countries:
        country_name = country.name.lower()
        if re.search(rf"\b{re.escape(country_name)}\b", normalized):
            return country.alpha_2

    for alias, code in COUNTRY_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return normalize_country_code(code)

    return None


def airport_country_matches(airport: dict, country_code: str) -> bool:
    """Check whether an airport belongs to the requested country.

    airportsdata normally stores an ISO country code. This function also
    tolerates alpha-3 codes and country names in the dataset.
    """
    wanted_alpha2 = normalize_country_code(country_code)
    airport_country = str(airport.get("country", "")).strip()
    airport_alpha2 = normalize_country_code(airport_country)

    if wanted_alpha2 and airport_alpha2:
        return wanted_alpha2 == airport_alpha2

    # Fallback for datasets that store the full country name.
    if wanted_alpha2:
        country = pycountry.countries.get(alpha_2=wanted_alpha2)
        if country and airport_country.casefold() == country.name.casefold():
            return True

    return False


def get_best_airport_for_country(country_code: str):
    """Return a preferred airport for a country, or rank available airports.

    The preferred mapping is a convenience default, not a guarantee that the
    airport is operating or has flights for a particular route/date.
    """
    alpha2 = normalize_country_code(country_code)
    if not alpha2:
        return None

    country = pycountry.countries.get(alpha_2=alpha2)
    alpha3 = country.alpha_3 if country else None

    # The existing mapping has both alpha-2 and alpha-3 keys.
    preferred = COUNTRY_MAIN_AIRPORT.get(alpha2) or COUNTRY_MAIN_AIRPORT.get(alpha3)
    if preferred and preferred in AIRPORTS:
        return preferred

    # If no preferred airport is configured, score airports in that country.
    candidates = []
    for iata, airport in AIRPORTS.items():
        if not iata or not airport_country_matches(airport, alpha2):
            continue

        name = str(airport.get("name", "")).lower()
        city = str(airport.get("city", "")).lower()
        score = 0
        if "international" in name:
            score += 50
        if "intl" in name:
            score += 40
        if city:
            score += 5
        candidates.append((score, iata))

    if not candidates:
        return None

    # Highest score first; IATA code makes ties deterministic.
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return candidates[0][1]


# clean_text() lowercases input, so normalize city-map keys once here.
# This fixes the previous mismatch where "Delhi" was compared with "delhi".
CITY_MAIN_AIRPORT_NORMALIZED = {
    clean_text(city): iata.upper()
    for city, iata in CITY_MAIN_AIRPORT.items()
}


def resolve_location_to_iata(location: str):
    """Convert a city, country, airport name, or IATA code to an IATA code.

    Lookup order:
      1. Validate a supplied 3-letter IATA code against the airport dataset.
      2. Check the preferred city-to-airport mapping.
      3. Check the preferred country-to-airport mapping.
      4. Search the airportsdata database for a matching city/airport name.

    Returns None when no reliable match is found; it does not invent a code.
    """
    if not location or not isinstance(location, str):
        return None

    raw_location = location.strip()
    if not raw_location:
        return None

    # Stage 1: A three-letter input is accepted only if it exists in AIRPORTS.
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)
    if not location_clean:
        return None

    # Stage 2: Use our explicit preferred airport for known cities.
    city_iata = CITY_MAIN_AIRPORT_NORMALIZED.get(location_clean)
    if city_iata and city_iata in AIRPORTS:
        return city_iata

    # Stage 3: Resolve a country and use its configured default airport.
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Stage 4: Search the airport database. Prefer exact city matches over
    # partial city/name matches, and prefer international airports on ties.
    city_matches = []
    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        city = clean_text(str(airport.get("city", "")))
        name = clean_text(str(airport.get("name", "")))
        score = 0

        if city == location_clean:
            score += 100
        elif location_clean and location_clean in city:
            score += 60

        if location_clean and location_clean in name:
            score += 30
        if "international" in str(airport.get("name", "")).lower():
            score += 10

        if score:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return city_matches[0][1]

    return None


def find_location_mentions(query: str):
    """Find known city/country mentions and return them in query order.

    Each result is (matched_text, start_position). Query order matters when
    inferring a route from a sentence that does not explicitly say "to".
    """
    q = query.lower()
    found = []

    # Search city names first, including aliases represented in the city map.
    for city in CITY_MAIN_AIRPORT:
        match = re.search(rf"\b{re.escape(city.lower())}\b", q)
        if match:
            found.append((city, match.start()))

    # Search country aliases. Keep longer aliases first to reduce ambiguity.
    for alias in sorted(COUNTRY_ALIASES, key=len, reverse=True):
        # Do not scan two-letter country codes as ordinary words. For example,
        # the alias "in" for India would otherwise match the preposition in
        # "flights in Japan". Users can still pass a country code directly to
        # resolve_location_to_iata().
        if len(alias) < 3:
            continue
        match = re.search(rf"\b{re.escape(alias.lower())}\b", q)
        if match:
            found.append((alias, match.start()))

    # Search official country names from pycountry.
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4:
            match = re.search(rf"\b{re.escape(name)}\b", q)
            if match:
                found.append((name, match.start()))

    # Deduplicate by normalized location while preserving its first position.
    unique = {}
    for location, position in found:
        key = clean_text(location)
        if key and (key not in unique or position < unique[key][1]):
            unique[key] = (location, position)

    return sorted(unique.values(), key=lambda item: item[1])


def _resolve_first_mention(mentions, start, end):
    """Resolve the first known location mention inside a query span."""
    for location, position in mentions:
        if start <= position < end:
            return resolve_location_to_iata(location)
    return None


def parse_route(query: str):
    """Extract departure and arrival IATA codes from a natural-language query.

    Return values:
      (None, None) -> global flight query or no route could be identified
      (DEP, ARR)   -> both ends of a route were identified
      (DEP, None)  -> only a departure location was identified
      (None, ARR)  -> only a destination was identified

    If only a destination is mentioned, DEFAULT_ORIGIN_IATA is used when it
    contains a valid IATA code. A country name such as "India" is not an IATA
    code and should not be stored in that environment variable.
    """
    if not query or not query.strip():
        return None, None

    q = query.strip()
    q_lower = q.lower()

    # Requests for worldwide/global data should not be narrowed to a route.
    global_keywords = (
        "all country", "all countries", "global flight", "global flights",
        "all flight", "all flights", "worldwide flight", "worldwide flights",
    )
    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Pattern A: explicit IATA route, e.g. "DAC to NRT", "dac to nrt",
    # "DEL-DXB", or "DEL -> DXB". Validate both codes against AIRPORTS.
    code_match = re.search(
        r"\b([A-Z]{3})\s*(?:to|->|-)\s*([A-Z]{3})\b",
        q,
        flags=re.IGNORECASE,
    )
    if code_match:
        dep = resolve_location_to_iata(code_match.group(1))
        arr = resolve_location_to_iata(code_match.group(2))
        if dep and arr:
            return dep, arr

    mentions = find_location_mentions(q)

    # Pattern B: "from X to Y". Resolve the known location mention in each
    # side of the route instead of passing the entire sentence to the lookup.
    from_match = re.search(r"\bfrom\b", q_lower)
    to_match = re.search(r"\bto\b", q_lower)
    if from_match and to_match and from_match.start() < to_match.start():
        dep = _resolve_first_mention(mentions, from_match.end(), to_match.start())
        # Destination ends before optional date/budget/trip details.
        tail = re.search(r"\b(?:on|for|under|including|with|at)\b", q_lower[to_match.end():])
        dest_end = to_match.end() + tail.start() if tail else len(q)
        arr = _resolve_first_mention(mentions, to_match.end(), dest_end)
        if dep or arr:
            return dep, arr

    # Pattern C: "to Y from X".
    if to_match and from_match and to_match.start() < from_match.start():
        arr = _resolve_first_mention(mentions, to_match.end(), from_match.start())
        tail = re.search(r"\b(?:on|for|under|including|with|at)\b", q_lower[from_match.end():])
        origin_end = from_match.end() + tail.start() if tail else len(q)
        dep = _resolve_first_mention(mentions, from_match.end(), origin_end)
        if dep or arr:
            return dep, arr

    # Pattern D: a sentence like "Plan a Japan trip from Bangladesh".
    # The location after "from" is the origin; another location before it
    # is treated as the destination.
    if from_match and mentions:
        dep = _resolve_first_mention(mentions, from_match.end(), len(q))
        arr = _resolve_first_mention(mentions, 0, from_match.start())
        if dep or arr:
            return dep, arr

    # Pattern E: only one location is mentioned.
    if len(mentions) == 1:
        location, _ = mentions[0]
        iata = resolve_location_to_iata(location)
        if re.search(r"\bfrom\b", q_lower):
            return iata, None

        # A destination-only request can use the configured default origin,
        # but only if the environment value is a real airport IATA code.
        default_origin = DEFAULT_ORIGIN_IATA
        if default_origin not in AIRPORTS:
            default_origin = None
        return default_origin, iata

    # Pattern F: two known locations without route words. Treat them as
    # origin then destination, following their order in the user's sentence.
    if len(mentions) >= 2:
        dep = resolve_location_to_iata(mentions[0][0])
        arr = resolve_location_to_iata(mentions[1][0])
        return dep, arr

    return None, None


def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()


def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    # Example route test: Bangladesh -> Japan (default airports DAC -> HND/PEK etc.)
    print("Parsed route:", parse_route("Plan a 7 days Japan trip from Bangladesh"))
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))