# cli_review.py
import os
import subprocess
import argparse
from code_review import codellama_review

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Code review CLI for git changes in another branch')
    parser.add_argument('--workdir', type=str, required=True, help='Working directory where the repository is located')
    parser.add_argument('--dev_branch', type=str, required=True, help='Development branch name')
    parser.add_argument('--changes_branch', type=str, required=True, help='Changes branch name')
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the code review prompt file')
    parser.add_argument('--output_file', type=str, default='review.md', help='Output file for the code reviews')
    parser.add_argument('--model', type=str, default='deepseek-r1:14b', help='Model name for Ollama')

    args = parser.parse_args()

    # Change to working directory
    os.chdir(args.workdir)

    try:
        # Get dev and changes branch names from params
        dev_branch = args.dev_branch
        changes_branch = args.changes_branch

        # Clean unstaged changes and checkout dev branch
        subprocess.run(['git', 'stash'], check=True)
        subprocess.run(['git', 'checkout', dev_branch], check=True)

        # Pull latest changes for both branches
        subprocess.run(['git', 'pull'], check=True)
        subprocess.run(['git', 'branch', '--track', changes_branch, f'origin/{changes_branch}'], check=True)
        subprocess.run(['git', 'checkout', changes_branch], check=True)
        subprocess.run(['git', 'pull'], check=True)

        # Get all files changed against dev branch
        result = subprocess.run(['git', 'diff', '--name-only', f'{dev_branch}...{changes_branch}'], capture_output=True, text=True)
        changed_files = result.stdout.split('\n')

        reviews = []
        for file in changed_files:
            if not file:  # Skip empty strings
                continue
            review = codellama_review(file, args.prompt_file, args.model)
            reviews.append(review)

        # Save all reviews to a single file
        with open(args.output_file, 'w') as f:
            for i, review in enumerate(reviews):
                f.write(f'### Review for {changed_files[i]}\n\n')
                f.write(review + '\n')

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return 1

if __name__ == '__main__':
    main()