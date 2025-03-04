#!/usr/bin/env python3
import argparse
import subprocess
import requests
import os

PROMPT_TEMPLATE = """
Actúa como un ingeniero de software senior. Realiza un code review del siguiente cambio.
Analiza posibles errores, violaciones de principios SOLID, problemas de rendimiento,
inconsistencias de estilo y posibles mejoras. Organiza tu respuesta en secciones claras.
Responde en español.

Código diff:
{diff}
"""

def get_git_output(command):
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error de Git: {e.output}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description='Code Review Automático usando Ollama')
    parser.add_argument('--model', default='codellama:7b', help='Modelo de Ollama a usar (default: codellama:7b)')
    parser.add_argument('--dev-branch', default='development', help='Rama base para comparación (default: development)')
    args = parser.parse_args()

    print(f"🔄 Obteniendo rama actual...")
    current_branch = get_git_output(['git', 'branch', '--show-current']).strip()
    
    if current_branch == args.dev_branch:
        print(f"⚠️  Ya estás en la rama {args.dev_branch}")
        exit(1)

    print(f"🔍 Comparando con rama '{args.dev_branch}'...")
    changed_files = get_git_output(['git', 'diff', '--name-only', args.dev_branch]).splitlines()
    
    if not changed_files:
        print("✅ No hay cambios detectados")
        exit(0)

    print(f"📁 Archivos modificados ({len(changed_files)}):")
    for file in changed_files:
        print(f" - {file}")

    print("\n" + "="*50 + "\n")

    for file in changed_files:
        print(f"🔎 Analizando: {file}")
        diff = get_git_output(['git', 'diff', args.dev_branch, '--', file])
        
        if not diff.strip():
            print("⚡ Sin cambios relevantes, saltando...")
            continue

        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': args.model,
                    'prompt': PROMPT_TEMPLATE.format(diff=diff),
                    'stream': False,
                    'options': {
                        'temperature': 0.2,
                        'num_predict': 1000
                    }
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Error API: {response.text}")
                continue

            review = response.json()['response']
            print(f"\n📝 Review para {file}:\n")
            print(review)
            print("\n" + "-"*50 + "\n")

        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar a Ollama. ¿Está ejecutándose?")
            exit(1)
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            continue

if __name__ == "__main__":
    main()
