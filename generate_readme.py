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
    headers["Accept"] = "application/vnd.github.mercy-preview+json"  # important for topics!
    repos = []
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        repos.extend(r.json())
        url = r.links.get("next", {}).get("url")
    return repos

def filter_repos(repos):
    filtered = []
    hide_topic = os.environ.get("HIDE_TOPIC", "").strip()
    for repo in repos:
        full_name = repo.get('full_name', 'unknown')
        fork = repo.get('fork', False)
        archived = repo.get('archived', False)
        topics = repo.get('topics', [])

        print(f"DEBUG: Checking repo: {full_name}")
        print(f"Fork: {fork}, Archived: {archived}, Topics: {topics}")

        # Exclude forks
        if fork and EXCLUDE_FORKS:
            print(f"Skipping {full_name} because it's a fork")
            continue

        # Exclude archived
        if archived and EXCLUDE_ARCHIVED:
            print(f"Skipping {full_name} because it's archived")
            continue

        # Exclude by topic
        if hide_topic and hide_topic in topics:
            print(f"Skipping {full_name} because it has the hide topic: {hide_topic}")
            continue

        print(f"Including repo in README")
        filtered.append(repo)

    return filtered


def categorize_repos(repos):
    categories = {
        "AI & ML": [],
        "LEGO Projects": [],
        "Automation": [],
        "Web & Apps": [],
        "CI\CD & Devops": [],
        "Fun & Magic": []
    }
    name = repo["name"]

    for repo in repos:
        repo_topics = repo.get("topics", [])

        # Trova i topic di categoria (quelli che iniziano con category-)
        cat_topics = [t for t in repo_topics if t.startswith("category-")]
        
        if "category-ai" in cat_topics:
            categories["AI & ML"].append(repo)
        elif "category-lego" in cat_topics:
            categories["LEGO Projects"].append(repo)
        elif "category-automation" in cat_topics:
            categories["Automation"].append(repo)
        elif "category-web" in cat_topics:
            categories["Web & Apps"].append(repo)
        elif "category-devops" in cat_topics:
            categories["CI\CD & Devops"].append(repo)
        elif name.lower() == "gianpy99":
            categories["CI\CD & Devops"].append(repo)
        else:
            categories["Fun & Magic"].append(repo)

    return categories

def md_table_row(repo):
    name = repo["name"]
    desc = repo.get("description", "No description").replace("|", "/")
    url = repo["html_url"]

    # Trova i topic tech-*
    tech_topics = [t.replace("tech-", "") for t in repo.get("topics", []) if t.startswith("tech-")]

    tech_str = ", ".join(tech_topics) if tech_topics else repo.get("language", "N/A")

    return f"| [{name}]({url}) | {desc} | {tech_str} |"

def format_repo_card(repo):
    name = repo["name"]
    url = repo["html_url"]
    topics = repo.get("topics", [])
    language = repo.get("language", "Unknown")
    
    # Default description and tech
    description = repo.get("description", "No description provided")
    tech = [language] if language else ["Unknown"]

    # Override for main repo if metadata file exists
    if name.lower() == "gianpy99":
        metadata_url = f"https://raw.githubusercontent.com/{repo['owner']['login']}/{name}/main/repo_metadata.json"
        try:
            resp = requests.get(metadata_url)
            if resp.status_code == 200:
                data = resp.json()
                description = data.get("description", description)
                tech = data.get("tech", tech)
                topics = data.get("topics", topics)
                # Topics as tags
                category_str = " ".join([f"`{t}`" for t in topics]) if topics else "`none`"
                tech_str = ", ".join(tech)
        except Exception as e:
            print(f"Could not load metadata for {name}: {e}")
    else:
        # Topics divisi in categorie e tech
        category_topics = [t.replace("category-", "") for t in topics if t.startswith("category-")]
        tech_topics = [t.replace("tech-", "") for t in topics if t.startswith("tech-")]
        category_str = ", ".join(category_topics) if category_topics else "none"
        tech_str = ", ".join(tech_topics) if tech_topics else language


    # Badge with shields.io
    badge = f"[![{name}](https://img.shields.io/badge/{name}-Repo-blue?style=for-the-badge&logo=github)]({url})"
    
    return (
        f"{badge}\n\n"
        f"🏷️ **Category:** {category_str}\n\n"
        f"💻 **Tech:** {tech_str}\n\n"
        f"📖 {description}\n\n\n---\n"
    )

def generate_readme(repos):
    content = "## 🚀 My Projects\n\n"
    for repo in repos:
        content += format_repo_card(repo)
    return content

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
        for repo in items[:TOP_N_REPOS]:
            parts.append(format_repo_card(repo))
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
