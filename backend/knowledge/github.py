import requests
from typing import List

class GitHubConnector:
    def __init__(self):
        self.data_store: List[str] = []

    def index_user_repos(self, username: str, token: str = None) -> int:
        """
        Fetches all public repos for a user and gathers deeper metadata.
        """
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        
        url = f"https://api.github.com/users/{username}/repos"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch repos: {response.status_code}")
                return 0
                
            repos = response.json()
            count = 0
            # Limit to top 5 repos for MVP performance
            for repo in repos[:5]:
                name = repo.get("name")
                desc = repo.get("description", "No description")
                lang = repo.get("language", "Unknown")
                
                # 1. Get README if possible
                readme_url = f"https://api.github.com/repos/{username}/{name}/readme"
                readme_content = ""
                r_res = requests.get(readme_url, headers=headers)
                if r_res.status_code == 200:
                    import base64
                    readme_content = base64.b64decode(r_res.json()["content"]).decode('utf-8', errors='ignore')[:500]
                
                knowledge_chunk = {
                    "source": f"github/{username}/{name}",
                    "tech_stack": lang,
                    "description": desc,
                    "readme_preview": readme_content.replace("\n", " ")
                }
                
                self.data_store.append(str(knowledge_chunk))
                count += 1
            
            return count
        except Exception as e:
            print(f"Error accessing GitHub: {e}")
            return 0

    def get_knowledge(self) -> List[str]:
        return self.data_store
