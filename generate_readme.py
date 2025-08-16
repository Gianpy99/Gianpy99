import os
import requests
import textwrap

# ===============================
# CONFIGURATION
# ===============================
USERNAME = os.getenv("PROFILE_USERNAME", "Gianpy99")
GH_TOKEN = os.getenv("GH_TOKEN")
TOP_N_REPOS = int(os.getenv("TOP_N_REPOS", 3))

EXCLUDE_FORKS = os.getenv("EXCLUDE_FORKS", "true").lower() == "true"
EXCLUDE_ARCHIVED = os.getenv("EXCLUDE_ARCHIVED", "true").lower() == "true"
HIDE_TOPIC = os.getenv("HIDE_TOPIC", "profile-hide")

# ===============================
# SEPARATOR OPTIONS
# ===============================
SEPARATORS = {
    "classic": "\n🌿✨🧙‍♂️✨🌿\n",
    "with_eagle": "\n🌿✨🧙‍♂️🦅✨🌿\n",
    "starry_night": "\n🌌✨🌠🧝‍♂️✨🌌\n",
    "forest_magic": "\n🍄🌺🦄🌿🧙‍♂️🌿\n",
    "adventure": "\n🏹🗡️⚔️🧙‍♂️⚔️🗡️🏹\n"
}
separator = SEPARATORS.get(os.getenv("SELECTED_SEPARATOR", "starry_night"), SEPARATORS["starry_night"])

# ===============================
# PROGRESS BAR OPTIONS
# ===============================
HOBBIT_STYLES = {
    "footsteps": ("🧙‍♂️", "👣", "🏔️"),
    "fire": ("🧙‍♂️", "🔥", "🏔️"),
    "blocks": ("🧙‍♂️", "🟩", "🏔️"),
    "mixed": ("🧙‍♂️", "🌿✨", "🏔️"),
}
TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", 10))
hobbit_choice = os.getenv("SELECTED_HOBBIT_STYLE", "footsteps")
HOBBIT, STEP, DEST = HOBBIT_STYLES.get(hobbit_choice, HOBBIT_STYLES["footsteps"])

def progress_bar(current, total=TOTAL_STEPS):
    steps_done = int((current / total) * TOTAL_STEPS)
    return f"{HOBBIT}{STEP * steps_done}{'▫️' * (TOTAL_STEPS - steps_done)}{DEST}"

# ===============================
# FETCH REPOS
# ===============================
def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated"
    headers = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}
    repos = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get("next", {}).get("url")
    return repos

def filter_repos(repos):
    filtered = []
    # after fetching repositories, e.g., using PyGithub
    for repo in repos:
       print(f"DEBUG: Checking repo: {repo.full_name}")
       print(f"       Fork: {repo.fork}, Archived: {repo.archived}, Topics: {repo.get_topics()}")

    # Exclude forks
       if repo.fork and os.environ.get("EXCLUDE_FORKS", "false") == "true":
          print(f"       Skipping because it's a fork")
          continue

    # Exclude archived
       if repo.archived and os.environ.get("EXCLUDE_ARCHIVED", "false") == "true":
          print(f"       Skipping because it's archived")
          continue

    # Exclude by topic
       hide_topic = os.environ.get("HIDE_TOPIC", "").strip()
       if hide_topic and hide_topic in repo.get_topics():
          print(f"       Skipping because it has the hide topic: {hide_topic}")
          continue

       print(f"       Including repo in README")

        filtered.append(repo)
    return filtered

def categorize_repos(repos):
    categories = {"AI & Machine Learning": [], "DevOps & Automation": [], "Tools & Utilities": [], "Other": []}
    for repo in repos:
        topics = repo.get("topics", [])
        if any(t in topics for t in ["ai", "ml", "tpu", "coral"]):
            categories["AI & Machine Learning"].append(repo)
        elif any(t in topics for t in ["devops", "automation", "cicd"]):
            categories["DevOps & Automation"].append(repo)
        elif any(t in topics for t in ["lego", "tool", "utility"]):
            categories["Tools & Utilities"].append(repo)
        else:
            categories["Other"].append(repo)
    return categories

def md_table_row(repo):
    name = f"[**{repo['name']}**]({repo['html_url']})"
    desc = (repo["description"] or "No description").replace("|", "\\|")
    lang = repo.get("language", "—")
    return f"| {name} | {desc} | {lang} |"

# ===============================
# BUILD README
# ===============================
def build_readme(repos):
    parts = []

    parts.append(f"<h1 align=\"center\">Hi there 👋, I'm {USERNAME} </h1>\n")
    parts.append("<p align=\"center\">\n  🚀 Engineer | 🔧 Maker | 🧠 Curious Technologist  \n</p>\n")

    parts.append("---\n")
    parts.append("### 👨‍💻 About Me\n")
    parts.append("I'm a hands-on engineer passionate about building test automation pipelines, embedded systems, and scalable development environments.\n")

    parts.append(separator)

    # Featured Projects
    categorized = categorize_repos(repos)
    parts.append("### 🌟 Featured Projects\n")
    for cat, items in categorized.items():
        if not items:
            continue
        parts.append(f"#### {cat}\n")
        parts.append("| Project | Description | Tech |\n|--------|-------------|------|\n")
        for repo in items[:TOP_N_REPOS]:
            parts.append(md_table_row(repo) + "\n")
        parts.append("\n")

    parts.append(separator)

    # Tech stack
    parts.append(textwrap.dedent("""
    ### 🛠 Tech Stack
    ```text
    Languages:    Python • Bash • Markdown • JavaScript (basic)
    Platforms:    Raspberry Pi • Windows • Linux • Docker
    Tools:        Jenkins • Git • CANape • REST APIs • OpenCV • VS Code
    AI/ML:        TensorFlow Lite • Google Coral TPU • Edge AI
    Web:          Flask • REST APIs • Web Development
    Finance:      Trading Automation • Crypto Markets
    ```
    """))

    parts.append(separator)

    # Progress bar section
    parts.append("### 🧙‍♂️ Quest Progress\n")
    for i in range(TOTAL_STEPS + 1):
        parts.append(progress_bar(i) + "\n")

    parts.append(separator)

    # Stats
    parts.append("### 📊 GitHub Stats\n")
    parts.append(f"![GitHub Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight)\n")
    parts.append(f"![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=tokyonight)\n")

    parts.append(separator)

    # Contact
    parts.append("### 📫 Let's Connect!\n")
    parts.append("- 💼 [LinkedIn](https://www.linkedin.com/in/gianpaolo-borrello)\n")
    parts.append(f"- 🌐 [GitHub Profile](https://github.com/{USERNAME})\n")
    parts.append("- 📬 Reach me: gianpaolo.borrello@gmail.com\n")

    return "\n".join(parts)

if __name__ == "__main__":
    repos = filter_repos(fetch_repos())
    readme_content = build_readme(repos)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ README.md generated successfully!")
