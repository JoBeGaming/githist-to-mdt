# Simple script to fetch the commits for a repository, and turn them into a MD Table.

# (c) JoBe, 2026


import git

import pathlib
import sys
import time


__all__ = [
    "get_commits",
    "format_iso",
    "make_table",
    "HEADER",
]


HEADER: str = """
<!--
Generated with 'python {}' on {}.

DO NOT EDIT.
-->

# Versionsgeschichte

| Autor | Datum | Nachricht |
| --- | --- | --- |
"""

DEFAULT_BRANCH: str = "HEAD" # IDK, shouldn't this be main or sum?



def get_commits(path: str, branch: str = DEFAULT_BRANCH) -> list[tuple[str, str, str, str | None]]:
    """
    Fetch the commit history for the repo with the given branch.
    The returned list is ordered newest to oldest, and each entry is a tuple of
    - name
    - date (iso)
    - message
    - commit url
    """

    repo = git.Repo(pathlib.Path(path))

    remote_url = ""
    if repo.remotes:
        remote_url = repo.remotes.origin.url

        if remote_url.startswith("git@github.com:"):
            remote_url = (
                remote_url.replace("git@github.com:", "https://github.com/")
                .replace(".git", "")
            )

        remote_url = remote_url.removesuffix(".git")

    commits = []

    for commit in repo.iter_commits(branch):
        author: str = commit.author.name # type: ignore
        date: str = commit.committed_datetime.isoformat() # type: ignore
        message: str = commit.message.strip() # type: ignore

        if remote_url:
            link = f"{remote_url}/commit/{commit.hexsha}"
        else:
            link = None

        commits.append((author, date, message, link))

    return commits


def format_iso(date: str) -> str:
    return f"{date[8:10]}.{date[5:7]}.{date[0:4]}"


def make_table(commits: list[tuple[str, str, str, str | None]], header: str = HEADER) -> str:
    result = HEADER.format(' '.join(sys.argv), time.strftime("%d.%m.%Y", time.localtime()))

    for author, date, message, url in commits:
        if not author in EXCLUDED_AUTHORS:
            result += f"| {AUTHMAP[author]} | {format_iso(date[:10])} | [`{message.replace("]", "").replace("\n", " ").replace("`", "'")}`]({url}) |\n"

    return result


if __name__ == "__main__":
    EXCLUDED_AUTHORS: list[str] = ["github-actions[bot]"]
    AUTHMAP: dict[str, str] = {
    }

    if any(helpflag in sys.argv for helpflag in ("-h", "--h", "-help", "--help")):
        print("Usage: gh2mdt [repository] [output (optional)]")
        exit()

    repo_path = sys.argv[1]
    result = make_table(get_commits(repo_path))

    result_path: str = DEFAULT_RESULT_NAME
    if len(sys.argv) > 2:
        result_path = sys.argv[2]

    with open(f"{repo_path}\\{result_path}", "w") as out:
        out.write(result)
