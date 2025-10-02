import argparse
import os

from loguru import logger

from .entities import ApiClient, Project

api_client = ApiClient(
    base_url=os.getenv("BASE_URL"),
    default_headers={"Authorization": f"Basic {os.getenv('USER_TOKEN')}"},
)

project = Project(api_client=api_client)

def create_project(args: argparse.Namespace):
    if not args.name:
        logger.error('Project "name" is not provided!')
        return
    project.create(args.name, args.description)


def get_projects():
    projects = project.get_projects()
    keys = ["id", "name", "description", "processingCounts"]

    if not project:
        return

    for _project in projects.json():
        for key in keys:
            _value = _project[key]
            if _value:
                print(f"{key}: {_value}")
        print()

def get_processings(args: argparse.Namespace):
    if not args.project_id:
        logger.error('Project "id" is not provided!')
        return

    processings = project.get_project_processings(args.project_id)
    keys = ["id", "name"]
    joined_keys = ["status", "percentCompleted", "cost"]

    if not processings:
        return

    for _processing in processings.json():
        for key in keys:
            print(f"{key}: {_processing[key]}")

        keys_value = [f"{key}: {_processing[key]}" for key in joined_keys]
        print(" | ".join(keys_value))
        if _processing["status"] == "FAILED":
            print("error: ", _processing["messages"])
        print()


def main():
    parser = argparse.ArgumentParser(description="Basic operations with projects (processing collections)")
    parser.add_argument('command', choices=['create', 'projects', 'processings'])
    parser.add_argument('-n', '--name', action='store')
    parser.add_argument('-d', '--description', action='store')
    parser.add_argument('--project-id', action='store')

    args = parser.parse_args()

    if args.command == 'create':
        create_project(args)

    if args.command == 'projects':
        get_projects()

    if args.command == 'processings':
        get_processings(args)


if __name__ == '__main__':
    main()
