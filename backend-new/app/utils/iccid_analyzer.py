"""
OSE Platform - ICCID Analyzer
Módulo para analizar ICCIDs de SIM (incluyendo IoT/globales)

Basado en el analizador proporcionado con tabla de IINs expandida.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any, List


# ═══════════════════════════════════════════════════════════════════════════
# ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class IINProfile:
    """Información asociada a un IIN (Issuer Identification Number)"""
    iin_prefix: str
    brand: str                 # Marca comercial
    operator: str              # Operador/plataforma
    country: str               # País principal o "Global"
    region: str                # Región geográfica
    use_case: str              # Caso de uso
    core_network: str          # Tipo de red
    notes: str                 # Notas
    confidence: str            # Nivel de confianza


# ═══════════════════════════════════════════════════════════════════════════
# TABLA DE IINs IoT / GLOBALES
# ═══════════════════════════════════════════════════════════════════════════

IIN_DB: Dict[str, IINProfile] = {}


def _register_iin(profile: IINProfile) -> None:
    """Registra un IIN en la tabla global"""
    IIN_DB[profile.iin_prefix] = profile


# ──────────────────────────────────────────────────────────────────────────
# IINs Globales IoT/M2M
# ──────────────────────────────────────────────────────────────────────────

_register_iin(IINProfile(
    iin_prefix="898822",
    brand="1NCE",
    operator="1NCE GmbH (sobre Deutsche Telekom)",
    country="Global (código 88)",
    region="Global",
    use_case="IoT global / M2M",
    core_network="LTE-M / NB-IoT / 2G/3G/4G",
    notes="SIM IoT global de 1NCE; tarifa plana típica de 10 años",
    confidence="confirmed"
))

_register_iin(IINProfile(
    iin_prefix="898830",
    brand="Tele2 IoT",
    operator="Tele2",
    country="Global (código 88)",
    region="Global",
    use_case="IoT global / M2M",
    core_network="LTE-M / NB-IoT / 2G/3G/4G",
    notes="Global SIM de Tele2 IoT",
    confidence="to-verify"
))

_register_iin(IINProfile(
    iin_prefix="8988247",
    brand="Vodafone IoT Global",
    operator="Vodafone",
    country="Global (código 88)",
    region="Global",
    use_case="IoT global / M2M",
    core_network="2G/3G/4G/LTE-M/NB-IoT",
    notes="Vodafone global M2M/IoT",
    confidence="to-verify"
))

_register_iin(IINProfile(
    iin_prefix="898823",
    brand="Vodafone IoT Global",
    operator="Vodafone",
    country="Global (código 88)",
    region="Global",
    use_case="IoT global / M2M",
    core_network="2G/3G/4G/LTE-M/NB-IoT",
    notes="Vodafone global M2M/IoT - variante 898823",
    confidence="confirmed"
))

_register_iin(IINProfile(
    iin_prefix="898921",
    brand="KORE Wireless",
    operator="KORE",
    country="Global",
    region="Global",
    use_case="IoT global",
    core_network="2G/3G/4G/LTE-M/NB-IoT",
    notes="Plataforma IoT global KORE",
    confidence="to-verify"
))

# ──────────────────────────────────────────────────────────────────────────
# IINs España
# ──────────────────────────────────────────────────────────────────────────

_register_iin(IINProfile(
    iin_prefix="893401",
    brand="Orange ES",
    operator="Orange España",
    country="España",
    region="Europa",
    use_case="Consumer / M2M",
    core_network="2G/3G/4G/5G",
    notes="Orange España - prefijo 893401",
    confidence="confirmed"
))

_register_iin(IINProfile(
    iin_prefix="893407",
    brand="Movistar ES",
    operator="Telefónica Móviles España",
    country="España",
    region="Europa",
    use_case="Consumer / M2M",
    core_network="2G/3G/4G/5G",
    notes="Movistar España - prefijo frecuente",
    confidence="confirmed"
))

_register_iin(IINProfile(
    iin_prefix="893460",
    brand="Vodafone ES",
    operator="Vodafone España",
    country="España",
    region="Europa",
    use_case="Consumer / M2M",
    core_network="2G/3G/4G/5G",
    notes="Vodafone España",
    confidence="confirmed"
))

_register_iin(IINProfile(
    iin_prefix="893465",
    brand="Orange ES / Simyo",
    operator="Orange España",
    country="España",
    region="Europa",
    use_case="Consumer / M2M / MVNO",
    core_network="2G/3G/4G/5G",
    notes="Orange ES y MVNOs",
    confidence="confirmed"
))

_register_iin(IINProfile(
    iin_prefix="893468",
    brand="MásMóvil / Yoigo",
    operator="MásMóvil",
    country="España",
    region="Europa",
    use_case="Consumer",
    core_network="2G/3G/4G/5G",
    notes="MásMóvil y Yoigo",
    confidence="to-verify"
))

# ──────────────────────────────────────────────────────────────────────────
# Otros países
# ──────────────────────────────────────────────────────────────────────────

_register_iin(IINProfile(
    iin_prefix="893330",
    brand="Orange FR",
    operator="Orange France",
    country="Francia",
    region="Europa",
    use_case="Consumer / M2M",
    core_network="2G/3G/4G/5G",
    notes="Orange Francia",
    confidence="to-verify"
))

_register_iin(IINProfile(
    iin_prefix="894420",
    brand="Vodafone UK",
    operator="Vodafone UK",
    country="Reino Unido",
    region="Europa",
    use_case="Consumer / M2M",
    core_network="2G/3G/4G/5G",
    notes="Vodafone Reino Unido",
    confidence="to-verify"
))

_register_iin(IINProfile(
    iin_prefix="894910",
    brand="Deutsche Telekom",
    operator="Deutsche Telekom",
    country="Alemania",
    region="Europa",
    use_case="Consumer / M2M",
    core_network="2G/3G/4G/5G",
    notes="Deutsche Telekom Alemania",
    confidence="to-verify"
))


# ═══════════════════════════════════════════════════════════════════════════
# CÓDIGOS DE PAÍS (E.118)
# ═══════════════════════════════════════════════════════════════════════════

_COUNTRY_CODES = {
    "1":  "Norteamérica (EE.UU./Canadá)",
    "33": "Francia",
    "34": "España",
    "39": "Italia",
    "44": "Reino Unido",
    "49": "Alemania",
    "52": "México",
    "55": "Brasil",
    "61": "Australia",
    "81": "Japón",
    "82": "Corea del Sur",
    "86": "China",
    "88": "Global / Servicios internacionales",
}


# ═══════════════════════════════════════════════════════════════════════════
# UTILIDADES INTERNAS
# ═══════════════════════════════════════════════════════════════════════════

def _sanitize_iccid(iccid: str) -> str:
    """Devuelve solo los dígitos del ICCID"""
    return "".join(ch for ch in iccid if ch.isdigit())


def _luhn_checksum_valid(iccid: str) -> bool:
    """Valida el ICCID usando el algoritmo de Luhn"""
    digits = [int(d) for d in iccid]
    check_digit = digits[-1]
    body = digits[:-1]

    total = 0
    double = True
    for d in reversed(body):
        if double:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        double = not double

    return (total + check_digit) % 10 == 0


def _guess_country(iccid: str) -> Dict[str, Optional[str]]:
    """Intenta inferir el código de país"""
    if not iccid.startswith("89") or len(iccid) < 4:
        return {"country_code": None, "country_name": None}

    # Probamos 3, 2 y 1 dígitos para el código de país
    for length in (3, 2, 1):
        if len(iccid) >= 2 + length:
            candidate = iccid[2:2 + length]
            if candidate in _COUNTRY_CODES:
                return {
                    "country_code": candidate,
                    "country_name": _COUNTRY_CODES[candidate],
                }

    return {"country_code": None, "country_name": None}


def _lookup_iin(iccid: str) -> Dict[str, Optional[Any]]:
    """Busca el IIN más largo que coincida"""
    max_len = min(8, len(iccid))
    for length in range(max_len, 5, -1):  # 8, 7, 6
        prefix = iccid[:length]
        if prefix in IIN_DB:
            profile = IIN_DB[prefix]
            return {
                "iin_prefix": prefix,
                "profile": profile,
            }

    return {
        "iin_prefix": None,
        "profile": None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def analyze_iccid(iccid: str) -> Dict[str, Any]:
    """
    Analiza un ICCID y devuelve información completa.

    Args:
        iccid: ICCID a analizar (puede contener espacios/guiones)

    Returns:
        Diccionario con toda la información del análisis
    """
    raw = iccid
    iccid = _sanitize_iccid(iccid)
    warnings: List[str] = []

    if not iccid:
        return {
            "iccid_raw": raw,
            "iccid": "",
            "error": "No se encontraron dígitos en el ICCID",
        }

    # Validar longitud
    length = len(iccid)
    valid_length = 18 <= length <= 22
    if not valid_length:
        warnings.append(
            f"Longitud atípica: {length} dígitos (esperado 18-22)"
        )

    # MII (Major Industry Identifier)
    mii = iccid[:2] if length >= 2 else None
    if mii != "89":
        warnings.append(
            f"MII distinto de '89' ({mii}). Puede no ser una SIM de telecom"
        )

    # País
    country_info = _guess_country(iccid)

    # IIN (Issuer Identification Number)
    iin_info = _lookup_iin(iccid)
    iin_prefix = iin_info["iin_prefix"]
    iin_profile_obj: Optional[IINProfile] = iin_info["profile"]  # type: ignore

    if iin_prefix is None:
        warnings.append(
            "No se encontró IIN en la tabla. "
            "Puede ser un operador desconocido"
        )
        account_number = iccid[2:-1] if length > 3 else None
    else:
        account_number = iccid[len(iin_prefix):-1] if length > len(iin_prefix) + 1 else None

    # Checksum
    checksum_digit = iccid[-1] if length >= 1 else None
    luhn_valid = _luhn_checksum_valid(iccid) if length >= 2 else False
    if not luhn_valid:
        warnings.append("El dígito de control (Luhn) no es válido")

    # Convertir perfil a dict
    iin_profile_dict = asdict(iin_profile_obj) if iin_profile_obj else None

    return {
        "iccid_raw": raw,
        "iccid": iccid,
        "length": length,
        "valid_length": valid_length,
        "mii": mii,
        "mii_meaning": "89 = Telecom / SIM" if mii == "89" else None,
        "country_code_guess": country_info["country_code"],
        "country_name_guess": country_info["country_name"],
        "iin_prefix": iin_prefix,
        "iin_profile": iin_profile_dict,
        "account_number": account_number,
        "checksum": checksum_digit,
        "luhn_valid": luhn_valid,
        "warnings": warnings,
    }


def get_available_iin_profiles() -> List[Dict[str, Any]]:
    """
    Devuelve lista de todos los perfiles IIN disponibles en la tabla.

    Returns:
        Lista de diccionarios con información de cada IIN
    """
    return [
        {
            **asdict(profile),
            "prefix": prefix
        }
        for prefix, profile in IIN_DB.items()
    ]
