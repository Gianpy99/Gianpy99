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
TOTAL_STEPS = 5
#HOBBIT = "🧝‍♂️"
#DESTINATION = "🏡"
#PATH_STEP = "·"

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


# ===============================
# SEPARATOR STYLES CONFIG
# ===============================
separator_styles = {
    "classic_magic":     "\n🌿✨🧙‍♂️✨🌿\n",       # Classic magical separator
    "flying_eagle":      "\n🌿✨🧙‍♂️🦅✨🌿\n",    # With flying eagle
    "starry_night":      "\n🌌✨🌠🧝‍♂️✨🌌\n",    # Starry night magical trail
    "forest_mystic":     "\n🍄🌺🦄🌿🧙‍♂️🌿\n",   # Forest + mystical creature
    "adventure_weapons": "\n🏹🗡️⚔️🧙‍♂️⚔️🗡️🏹\n" # Adventure + weapon theme
}

# Pick your separator style
selected_separator = "starry_night"
separator = separator_styles[selected_separator]

# Example usage
# readme_content += separator

for repo in repos_to_list:
    readme_content += f"- [{repo.name}]({repo.html_url}): {repo.description or 'No description'}{separator}"

# ===============================
# HOBBIT PROGRESS BAR CONFIG
# ===============================
# Make sure TOTAL_STEPS and repos_to_list are defined before this block
current_progress = min(len(repos_to_list), TOTAL_STEPS)

# Define different progress bar styles
progress_styles = {
    "hobbit_walk":      "🧝‍♂️" + "·" * current_progress + "🏡" + "·" * (TOTAL_STEPS - current_progress),
    "hobbit_hill":      "🧝‍♂️" + "⛰️" * current_progress + "🏡" + "·" * (TOTAL_STEPS - current_progress),
    "hobbit_shadowfax": "🧙‍♂️🐎" + "·" * current_progress + "🏡" + "·" * (TOTAL_STEPS - current_progress),
    "hobbit_stars":     "🧝‍♂️✨🌠" + "·" * current_progress + "🏡" + "✨🌌" * (TOTAL_STEPS - current_progress),
    "hobbit_creatures": "🧝‍♂️🕊️🦋" + "·" * current_progress + "🏡" + "·" * (TOTAL_STEPS - current_progress)
}

# Choose your progress style
selected_style = "hobbit_shadowfax"
progress_bar = progress_styles[selected_style]

# Add progress bar to README content (wrapped in a code block for alignment)
readme_content += f"\n## 🗺️ Journey Progress\n\n```\n{progress_bar}\n```\n"

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
