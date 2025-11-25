"""
Script de prueba para validar generación de ICCIDs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.utils.iccid_utils import generate_iccid_range

# Prueba con el ejemplo del usuario
iccid_start = "89882390001334701795"
iccid_end = "89882390001334801785"

print("="*70)
print("PRUEBA DE GENERACIÓN DE ICCIDS")
print("="*70)
print(f"\nICCID Inicial: {iccid_start}")
print(f"ICCID Final:   {iccid_end}")
print()

# Extraer bodies para mostrar el cálculo
start_body = int(iccid_start[:-1])
end_body = int(iccid_end[:-1])
expected_count = end_body - start_body + 1

print(f"Body Inicial: {start_body}")
print(f"Body Final:   {end_body}")
print(f"Diferencia:   {end_body} - {start_body} + 1 = {expected_count:,}")
print()

# Generar rango
print("Generando ICCIDs...")
try:
    iccid_range = generate_iccid_range(iccid_start, iccid_end)
    total_generated = len(iccid_range)

    print(f"\n[OK] ICCIDs generados: {total_generated:,}")

    # Verificar que coincide con el esperado
    if total_generated == expected_count:
        print(f"[OK] CORRECTO: El total coincide con el esperado ({expected_count:,})")
    else:
        print(f"[ERROR] Se esperaban {expected_count:,} pero se generaron {total_generated:,}")

    # Mostrar primeros y últimos 3 ICCIDs
    print(f"\nPrimeros 3 ICCIDs:")
    for i, (iccid_full, body, check) in enumerate(iccid_range[:3], 1):
        print(f"  {i}. {iccid_full} (body: {body}, check: {check})")

    print(f"\nÚltimos 3 ICCIDs:")
    for i, (iccid_full, body, check) in enumerate(iccid_range[-3:], total_generated-2):
        print(f"  {i}. {iccid_full} (body: {body}, check: {check})")

    print("\n" + "="*70)
    print("RESULTADO: [OK] PRUEBA EXITOSA")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR]: {e}")
    print("="*70)
    import traceback
    traceback.print_exc()
