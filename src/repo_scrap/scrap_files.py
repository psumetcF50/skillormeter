import os
from pathlib import Path
from git import Repo
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
ALLOWED_EXTENSIONS = [".py", ".md", ".java", ".js", ".ts"]

def read_repo_files(repo_path: str, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", "node_modules"]

    repo_path = Path(repo_path).resolve()
    file_contents = {}

    for root, dirs, files in os.walk(repo_path):
        # skip excluded dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                filepath = Path(root) / file
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        file_contents[str(filepath)] = f.read()
                except Exception as e:
                    print(f"Could not read {filepath}: {e}")
    return file_contents



def get_commit_file_changes(repo_path: str, max_commits=100):
    repo = Repo(repo_path)
    NULL_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    NULL_TREE = repo.tree(NULL_TREE_SHA)

    commit_file_data = []

    for commit in repo.iter_commits("main", max_count=max_commits):  # change branch if needed
        parent = commit.parents[0] if commit.parents else NULL_TREE
        diffs = commit.diff(parent, create_patch=True)

        for diff in diffs:
            file_path = diff.b_path or diff.a_path
            if file_path is None:
                continue

            # Filter by allowed extensions
            if not any(file_path.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue

            # Patch text
            try:
                patch_text = diff.diff.decode("utf-8", errors="ignore")
            except Exception:
                patch_text = ""

            # File content at this commit
            try:
                blob = commit.tree / file_path
                file_content = blob.data_stream.read().decode("utf-8", errors="ignore")
            except Exception:
                file_content = ""

            commit_file_data.append({
                "commit_hash": commit.hexsha,
                "author": commit.author.name,
                "date": commit.committed_datetime.isoformat(),
                "commit_message": commit.message.strip(),
                "file_path": file_path,
                "patch": patch_text,
                "file_content": file_content
            })

    return commit_file_data



def map_authors_to_files(file_contents, commit_file_data):
    author_file_map = {}

    for commit in commit_file_data:
        author = commit["author"]
        file_path = commit["file_path"]

        file_text = file_contents.get(file_path, "")  # fallback if file missing

        entry = {
            "file_path": file_path,
            #"file_content": file_text,
            #"commit_message": commit["message"],
            #"commit_hash": commit["hash"],
            #"commit_date": commit["date"],
            #"change_type": commit["change_type"],
            "patch": commit["patch"],
        }

        if author not in author_file_map:
            author_file_map[author] = []
        author_file_map[author].append(entry)

    return author_file_map

def chunk_author_changes(author_file_map, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_data = []

    for author, entries in author_file_map.items():
        for entry in entries:
            # determine file type
            file_type = entry['file_path'].split('.')[-1] if '.' in entry['file_path'] else 'txt'

            # combine patch + file content to include actual changes
            text_to_chunk = f"Patch:\n{entry['patch']}"

            chunks = splitter.split_text(text_to_chunk)
            for chunk in chunks:
                chunked_data.append({
                    "author": author,
                    "file_type": file_type,
                    "chunk": chunk
                })
    return chunked_data

def save_chunked_data(chunked_data, filepath="chunked_data.json"):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chunked_data, f, ensure_ascii=False, indent=2)


# --- Step 2: Read chunked data from JSON file ---
def load_chunked_data(filepath="chunked_data.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__=="__main__":
    repo_path = "./"
    data_file_path = "git_chunked_data.json"

    files = read_repo_files(repo_path)
    commit_file_data = get_commit_file_changes(repo_path, max_commits=50)
    author_file_map = map_authors_to_files(files, commit_file_data)
    chunks = chunk_author_changes(author_file_map)
    save_chunked_data(chunks, data_file_path)
    print("done")

    # print a preview
    #for author, entries in author_file_map.items():
    #    print(f"\nAuthor: {author}")
    #    for e in entries[:2]:  # preview first 2 per author
    #        print(f"- File: {e['file_path']}")
    #        print(f"  Commit: {e['commit_hash'][:7]} - {e['commit_message']}")
    #        #print(f"  Patch:\n{e['patch'][:200]}...\n")
    #        print(f"  Patch:\n{e['patch']}...\n")
#