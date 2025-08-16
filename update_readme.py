import os
from github import Github

# ----------------------------
# CONFIG
# ----------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = "Gianpy99"
TAG_FILTER = "show-readme"  # Only include repos with this topic
IMAGE_PATH = "assets/gandalf_shadowfax.png"  # Path in your repo

# Progress bar settings
TOTAL_STEPS = 10
HOBBIT = "🧝‍♂️"
DESTINATION = "🏡"
PATH_STEP = "·"

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
user = g.get_user(GITHUB_USERNAME)

# ----------------------------
# FETCH REPOS
# ----------------------------
repos_to_list = []
for repo in user.get_repos():
    topics = repo.get_topics()
    if TAG_FILTER in topics:
        repos_to_list.append(repo)

# ----------------------------
# GENERATE README CONTENT
# ----------------------------
readme_content = f"""# 🧙‍♂️ My Magical GitHub

![Gandalf & Shadowfax]({IMAGE_PATH})

> "All we have to decide is what to do with the time that is given us." – Gandalf

---

## ✨ Projects

"""

separator = "\n🌿✨🧙‍♂️✨🌿\n"

for repo in repos_to_list:
    readme_content += f"- [{repo.name}]({repo.html_url}): {repo.description or 'No description'}{separator}"

# Hobbit progress bar
current_progress = min(len(repos_to_list), TOTAL_STEPS)
progress_bar = HOBBIT + PATH_STEP * current_progress + DESTINATION + PATH_STEP * (TOTAL_STEPS - current_progress)
readme_content += f"\n## 🗺️ Journey Progress\n\n{progress_bar}\n"

# Example badges
readme_content += """

---

![GitHub stars](https://img.shields.io/github/stars/Gianpy99/Gianpy99?style=for-the-badge&color=blueviolet)
![Python version](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge)
"""

# ----------------------------
# WRITE README
# ----------------------------
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("✅ README.md updated successfully!")
