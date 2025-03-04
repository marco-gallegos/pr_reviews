# code_review_function.py
import os
import ollama as Ollama
import subprocess

def get_git_output(command):
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error de Git: {e.output}")
        exit(1)

def codellama_review(file_path, prompt_file, model='codellama:7b'):
    # Read the prompt file content
    with open(prompt_file, 'r') as f:
        prompt_template = f.read()

    print(file_path)
    # Get the file changes compared to dev branch
    result = get_git_output(['git', 'diff', 'development', '--', file_path])

    if not result.strip():
        print("No hay cambios en el archivo")
        return

    file_changes = result

    # Read the file content
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # print(file_changes)

    # Replace placeholders in prompt with actual content
    prompt = prompt_template.replace('{{changes}}', file_changes)
        # .replace('{{content}}', file_content)
    # print(prompt)

    # Run code review using Ollama API
    client = Ollama.Client(
        host='http://192.168.0.111:11434',
        headers={'x-some-header': 'some-value'}
    )
    response = client.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        stream=False
    )
    print(response.message)

    return response.message.content