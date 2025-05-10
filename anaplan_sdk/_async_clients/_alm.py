from asyncio import sleep
import logging
import warnings

import httpx

from anaplan_sdk._base import _AsyncBaseClient
from anaplan_sdk.exceptions import AnaplanActionError
from anaplan_sdk.models import ModelRevision, Revision, SyncTask, TaskStatus, User

warnings.filterwarnings("always", category=DeprecationWarning)
logger = logging.getLogger("anaplan_sdk")


class _AsyncAlmClient(_AsyncBaseClient):
    def __init__(self, client: httpx.AsyncClient, model_id: str, retry_count: int) -> None:
        self._client = client
        self._url = f"https://api.anaplan.com/2/0/models/{model_id}/alm"
        super().__init__(retry_count, client)

    async def list_users(self) -> list[User]:
        """
        Lists all the Users in the authenticated users default tenant.
        :return: The List of Users.
        """
        warnings.warn(
            "`list_users()` on the ALM client is deprecated and will be removed in a "
            "future version. Use `list_users()` on the Audit client instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        return [
            User.model_validate(e)
            for e in (await self._get("https://api.anaplan.com/2/0/users")).get("users")
        ]

    async def get_syncable_revisions(self, source_model_id: str) -> list[Revision]:
        """
        Use this call to return the list of revisions from your source model that can be
        synchronized to your target model.

        The returned list displays in descending order, by creation date and time. This is
        consistent with how revisions are displayed in the user interface (UI).
        :param source_model_id: The ID of the source model.
        :return: A list of revisions that can be synchronized to the target model.
        """
        revs = (
            await self._get(f"{self._url}/syncableRevisions?sourceModelId={source_model_id}")
        ).get("revisions", [])
        return [Revision.model_validate(e) for e in revs] if revs else []

    async def get_latest_revision(self) -> list[Revision]:
        """
        Use this call to return the latest revision for a specific model. The response is in the
        same format as in Getting a list of syncable revisions between two models.

        If a revision exists, the return list should contain one element only which is the
        latest revision.
        :return: The latest revision for a specific model.
        """
        return [
            Revision.model_validate(e)
            for e in (await self._get(f"{self._url}/latestRevision")).get("revisions", [])
        ]

    async def get_sync_tasks(self) -> list[SyncTask]:
        """
        Use this endpoint to return a list of sync tasks for a target model, where the tasks are
        either in progress, or they were completed within the last 48 hours.

        The list is in descending order of when the tasks were created.
        :return: A list of sync tasks for a target model.
        """
        return [
            SyncTask.model_validate(e)
            for e in (await self._get(f"{self._url}/syncTasks")).get("tasks", [])
        ]

    async def get_revisions(self) -> list[Revision]:
        """
        Use this call to return a list of revisions for a specific model.
        :return: A list of revisions for a specific model.
        """
        return [
            Revision.model_validate(e)
            for e in (await self._get(f"{self._url}/revisions")).get("revisions", [])
        ]

    async def get_models_for_revision(self, revision_id: str) -> list[ModelRevision]:
        """
        Use this call when you need a list of the models that had a specific revision applied
        to them.
        :param revision_id: The ID of the revision.
        :return: A list of models that had a specific revision applied to them.
        """
        return [
            ModelRevision.model_validate(e)
            for e in (await self._get(f"{self._url}/revisions/{revision_id}/appliedToModels")).get(
                "appliedToModels", []
            )
        ]

    async def run_sync(
        self, source_model_id: str, source_revision_id: str, target_revision_id: str
    ) -> TaskStatus:
        """
        Runs the ALM model sync to update the current model from the source model
        and source revision.  The target_revision must be the current model's latest revision.
        When the sync is complete, the current model's latest revision will be
        the source revision.
        :param source_model_id: The identifier of the model with the desired revision.
                                Typically this is either a development model or a test model.
        :param source_revision: The revision on the source model with the desired changes.
                                This must be after the target revision, but need not be the
                                latest revision in the source model.
        :param target_revision: The latest revision in the current model.
        :return: The status of the model sync activity
        """
        task_id = await self.invoke_sync(source_model_id, source_revision_id, target_revision_id)
        task_status = await self.get_task_status(task_id)

        while task_status.task_state != "COMPLETE":
            await sleep(self.status_poll_delay)
            task_status = await self.get_task_status(task_id)

        if task_status.task_state == "COMPLETE" and not task_status.result.successful:
            raise AnaplanActionError(f"Task '{task_id}' completed with errors.")

        logger.info(f"Task '{task_id}' completed successfully.")
        return task_status

    async def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Retrieves the status of the specified ALM sync task.
        :param task_id: The identifier of the spawned ALM sync task.
        :return: The status of the ALM sync task.
        """
        return TaskStatus.model_validate(
            (await self._get(f"{self._url}/syncTasks/{task_id}")).get("task")
        )

    async def invoke_sync(
        self, source_model_id: str, source_revision_id: str, target_revision_id: str
    ) -> str:
        """
        You may want to consider using `run_sync()` instead.

        Invokes the specified ALM model sync action and returns the spawned Task identifier.
        This is useful if you want to handle the Task status yourself or if you want to run
        multiple model sync actions in parallel.
        :param source_model_id: The identifier of the model with the desired revision.
                                Typically this is either a development model or a test model.
        :param source_revision: The revision on the source model with the desired changes.
                                This must be after the target revision, but need not be the
                                latest revision in the source model.
        :param target_revision: The latest revision in the current model.
        :return: The identifier of the spawned task.
        """
        response = await self._post(
            f"{self._url}/syncTasks",
            json={
                "sourceRevisionId": source_revision_id,
                "sourceModelId": source_model_id,
                "targetRevisionId": target_revision_id,
            },
        )
        task_id = response.get("task").get("taskId")
        logger.info(
            (
                f"Invoked ALM sync from revision '{target_revision_id}' "
                f"to model '{source_model_id}' revision '{source_revision_id}', "
                f"spawned Task: '{task_id}'."
            )
        )
        return task_id
