
    import os
    import datetime
    from typing import List, Dict
    from github import Github, GithubException

    # ===============================
    # CONFIGURATION
    # ===============================
    USERNAME = os.getenv("PROFILE_USERNAME", "Gianpy99")
    TOKEN = os.getenv("GH_TOKEN")  # set via GitHub Actions secret
    TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", "10"))          # progress bar granularity
    TOP_N_REPOS = int(os.getenv("TOP_N_REPOS", "3"))           # top starred per category
    SELECTED_SEPARATOR = os.getenv("SELECTED_SEPARATOR", "starry_night")
    SELECTED_HOBBIT_STYLE = os.getenv("SELECTED_HOBBIT_STYLE", "blocks")  # 'blocks' or 'dots'
    HIDE_TOPIC = os.getenv("HIDE_TOPIC", "profile-hide")       # add this topic to any repo you want to hide
    EXCLUDE_FORKS = os.getenv("EXCLUDE_FORKS", "true").lower() == "true"
    EXCLUDE_ARCHIVED = os.getenv("EXCLUDE_ARCHIVED", "true").lower() == "true"

    # Category topics mapping (lowercase); add/remove as you like
    CATEGORY_TOPICS = {
        "AI & Machine Learning": {"ai", "ml", "machine-learning", "deep-learning", "tensor", "coral", "tflite"},
        "DevOps & Automation": {"devops", "automation", "cicd", "ci", "jenkins", "docker", "pipeline", "raspberry-pi"},
        "Tools & Utilities": {"tools", "utility", "script", "cli", "converter", "flask", "web"}
    }

    FEATURED_MARKERS = {"featured"}  # either repo topic OR repo label named 'featured'

    # ===============================
    # SEPARATOR OPTIONS
    # ===============================
    SEPARATORS = {
        "classic_magic":     "\n🌿✨🧙‍♂️✨🌿\n",
        "flying_eagle":      "\n🌿✨🧙‍♂️🦅✨🌿\n",
        "starry_night":      "\n🌌✨🌠🧝‍♂️✨🌌\n",
        "forest_mystic":     "\n🍄🌺🦄🌿🧙‍♂️🌿\n",
        "adventure_weapons": "\n🏹🗡️⚔️🧙‍♂️⚔️🗡️🏹\n"
    }
    SEPARATOR = SEPARATORS.get(SELECTED_SEPARATOR, SEPARATORS["starry_night"])

    # ===============================
    # HOBBIT PROGRESS BAR (two styles)
    # ===============================
    def progress_bar_dots(completed: int, total: int) -> str:
        completed = max(0, min(completed, total))
        return "🧙‍♂️🐎" + "·" * completed + "🏡" + "·" * (total - completed)

    def progress_bar_blocks(completed: int, total: int) -> str:
        completed = max(0, min(completed, total))
        return "🧙‍♂️🐎" + "🟩" * completed + "⬜" * (total - completed) + "🏡"

    def make_progress_bar(completed: int, total: int, style: str) -> str:
        return progress_bar_blocks(completed, total) if style == "blocks" else progress_bar_dots(completed, total)

    # ===============================
    # CI/CD PROGRESS (fun placeholder)
    # ===============================
    def cicd_progress_line(step: int = 0, total_steps: int = 12) -> str:
        phases = ["⏳ Build", "⚙️ Test", "🧪 QA", "🔐 Scan", "📦 Package", "🚀 Deploy"]
        phase = phases[step % len(phases)]
        filled = "🔹" * step
        empty = "▫️" * (total_steps - step)
        return f"{filled}{empty}  {phase}"

    # ===============================
    # TABLE HELPERS
    # ===============================
    def md_table_header() -> str:
        return "| Project | Description | Stars | Topics |\n|--------|-------------|------:|--------|\n"

    def md_table_row(repo) -> str:
        desc = (repo.description or "-").replace("\n", " ").strip()
        topics = ", ".join(repo.get_topics() or [])
        return f"| [**{repo.name}**]({repo.html_url}) | {desc} | ⭐ {repo.stargazers_count} | {topics} |"

    # ===============================
    # MAIN
    # ===============================
    def main():
        if not TOKEN:
            raise SystemExit("GH_TOKEN is not set. Add it as a GitHub Actions secret.")
        gh = Github(TOKEN)
        user = gh.get_user(USERNAME)
        repos = list(user.get_repos(visibility="public"))

        # Filter
        public_repos = []
        for r in repos:
            try:
                topics = set([t.lower() for t in (r.get_topics() or [])])
            except GithubException:
                topics = set()
            if EXCLUDE_FORKS and r.fork:
                continue
            if EXCLUDE_ARCHIVED and r.archived:
                continue
            if HIDE_TOPIC and HIDE_TOPIC in topics:
                continue
            public_repos.append(r)

        # Featured detection (topic OR label 'featured')
        featured = []
        backlog = []
        for r in public_repos:
            topics = set([t.lower() for t in (r.get_topics() or [])])
            is_featured = bool(FEATURED_MARKERS & topics)
            if not is_featured:
                # check repo labels (issue labels namespace)
                try:
                    labels = {lb.name.lower() for lb in r.get_labels()}
                    is_featured = bool(FEATURED_MARKERS & labels)
                except GithubException:
                    pass
            if is_featured:
                featured.append(r)
            else:
                backlog.append(r)

        # Category buckets by topics
        buckets: Dict[str, List] = {k: [] for k in CATEGORY_TOPICS}
        other_bucket = []
        for r in public_repos:
            topics = set([t.lower() for t in (r.get_topics() or [])])
            placed = False
            for cat, keys in CATEGORY_TOPICS.items():
                if topics & keys:
                    buckets[cat].append(r)
                    placed = True
                    break
            if not placed:
                other_bucket.append(r)

        # Sort by stars and clamp
        def sort_star_clip(lst):
            return sorted(lst, key=lambda x: x.stargazers_count, reverse=True)[:TOP_N_REPOS]

        for cat in buckets:
            buckets[cat] = sort_star_clip(buckets[cat])
        featured = sort_star_clip(featured)
        backlog_sorted = sorted([r for r in backlog if r not in featured], key=lambda x: x.stargazers_count, reverse=True)

        # Progress bars
        completed_steps = min(len(public_repos), TOTAL_STEPS)
        hobbit_bar = make_progress_bar(completed_steps, TOTAL_STEPS, SELECTED_HOBBIT_STYLE)

        # CI/CD fun progress based on day-of-year
        doy = int(datetime.datetime.utcnow().strftime("%j"))
        cicd_step = doy % 12
        cicd_line = cicd_progress_line(cicd_step, 12)

        # Build README
        parts = []

        parts.append(f"""<h1 align="center">Hi there 👋, I'm Gianpaolo</h1>

<p align="center">
  🚀 Engineer | 🔧 Maker | 🧠 Curious Technologist
</p>

{SEPARATOR}
### 👨‍💻 About Me

I'm a hands-on engineer passionate about building test automation pipelines, embedded systems, and scalable development environments. I love turning LEGO bricks, Raspberry Pis, and CI/CD tools into real-world validation platforms.

- 🔍 Focused on **HIL testing**, **DevOps for embedded**, and **automation**
- 🧰 Tools I work with: Python, Docker, Jenkins, Raspberry Pi, REST APIs, CAN tools
- 🎯 Currently building: a fully automated CI/CD test platform
""")

        parts.append(SEPARATOR)
        parts.append("### 🌟 Featured Projects\n")
        if featured:
            parts.append(md_table_header())
            for r in featured:
                parts.append(md_table_row(r))
        else:
            parts.append("_Tag a repo with the **featured** topic or label to showcase it here._")

        # Category sections
        for cat_name, repo_list in buckets.items():
            if not repo_list:
                continue
            parts.append(SEPARATOR)
            parts.append(f"#### {cat_name}\n")
            parts.append(md_table_header())
            for r in repo_list:
                parts.append(md_table_row(r))

        # Backlog (exclude private automatically by fetch)
        if backlog_sorted:
            parts.append(SEPARATOR)
            parts.append("### 📦 Backlog / Other Projects\n")
            for r in backlog_sorted:
                parts.append(f"- [{r.name}]({r.html_url}): {r.description or 'No description'}")


        parts.append(SEPARATOR)
        parts.append("### 🗺️ Journey Progress\n\n" + hobbit_bar + "\n")

        parts.append(SEPARATOR)
        parts.append("### 🔄 CI/CD Status\n\n" + cicd_line + "\n")

        parts.append(SEPARATOR)
        parts.append(textwrap.dedent(f"""        ### 🛠 Tech Stack
        ```text
        Languages:    Python • Bash • Markdown • JavaScript (basic)
        Platforms:    Raspberry Pi • Windows • Linux • Docker
        Tools:        Jenkins • Git • CANape • REST APIs • OpenCV • VS Code
        AI/ML:        TensorFlow Lite • Google Coral TPU • Edge AI
        Web:          Flask • REST APIs • Web Development
        Finance:      Trading Automation • Crypto Markets
        ```
        """))

        parts.append(SEPARATOR)
        parts.append("""### 🏆 What I'm Working On

- 🤖 **Edge AI Development**: On-device inference with Coral TPU
- 🔄 **CI/CD Automation**: Building robust validation pipelines
- 📈 **Trading Automation**: Algorithmic crypto trading
- 🎯 **Educational Tools**: Interactive learning platforms with AI
""")

        parts.append(SEPARATOR)
        parts.append(f"""### 📊 GitHub Stats

![GitHub Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=tokyonight)
""")

        parts.append(SEPARATOR)
        parts.append(f"""### 📫 Let's Connect!

- 💼 [LinkedIn](https://www.linkedin.com/in/gianpaolo-borrello)
- 🌐 [GitHub Profile](https://github.com/{USERNAME})
- 📬 Reach me: gianpaolo.borrello@gmail.com

<sub>Thanks for visiting! I'm always open to collaborations, interesting side projects, and improving systems through automation.</sub>

*Auto-generated on {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
""")

        readme = "\n".join(parts).strip() + "\n"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme)

        print("✅ README.md updated. Public repos considered:", len(public_repos))

    if __name__ == "__main__":
        main()
