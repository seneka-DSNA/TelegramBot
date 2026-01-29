import re

from access_code_repository import AccessCodeRepository

ACCESS_CODE_REGEX = re.compile(r"^[A-Z0-9]{10}$")


def main():
    repo = AccessCodeRepository()

    print("=== Crear Access Code ===")

    while True:
        code = input("Introduce access_code (10 caracteres A-Z0-9): ").strip().upper()

        # Validación de formato
        if not ACCESS_CODE_REGEX.match(code):
            print("❌ Código inválido. Debe tener exactamente 10 caracteres A-Z0-9.")
            continue

        # Validación de duplicado
        if repo.exists_and_unused(code):
            print("❌ El código ya existe y no ha sido usado. Introduce otro.")
            continue

        # Guardar en DB
        try:
            repo.create(code)
        except Exception as e:
            # Protección extra por si hay carrera o duplicado inesperado
            print("❌ Error al guardar el código. Inténtalo de nuevo.")
            continue

        print(f"✅ Access code '{code}' creado correctamente.")
        break


if __name__ == "__main__":
    main()

