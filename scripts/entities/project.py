from typing import Optional

from loguru import logger

from .api_client import ApiClient


class Project:
    def __init__(self, api_client: ApiClient = None, id: Optional[str] = None):
        self.api_client = api_client
        self.id = id

    def create(self, name: str, description: Optional[str] = None):
        logger.info("Creating project...")

        response = self.api_client.post(
            "/projects", json={"name": name, "description": description}
        )

        if response.status_code == 200:
            logger.info(f"Successfully created project {response.json()['id']}")
            return response
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when creating project: {_msg}")
            return None

    def get_projects(self):
        response = self.api_client.get("/projects")

        if response.status_code == 200:
            logger.info("Successfully recieved projects")
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting projects: {_msg}")
            return None

        return response

    def get_project_processings(self, project_id: Optional[str] = None):
        project_id = project_id or self.id
        if not project_id:
            logger.error('Project "id" is required!')
            return None

        response = self.api_client.get(f"/projects/{project_id}/processings")
        if response.status_code == 200:
            if response.json() != []:
                logger.info("Project processings succesfully received")
                return response
            else:
                logger.error("There are no processings in this project")
                return None
        else:
            _msg = f"{response.status_code} {response.reason} {response.text}"
            logger.error(f"Error when getting project processings: {_msg}")
            return None

