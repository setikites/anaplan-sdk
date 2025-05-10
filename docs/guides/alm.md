The purpose of the Application Lifecycle Management (ALM) API is to make model change management more scalable,
automatable, and integrate with other systems.

For details on required subscriptions and what you might want to use the ALM API for, refer to
[the Documentation](https://help.anaplan.com/application-lifecycle-management-0406d4dd-3e8d-40c0-be2f-1c34c1caeebf).

## Accessing the Namespace

All the methods for the ALM APIs reside in a different namespace for better API navigability and
comprehensiveness, but are accessible through the same client for convenience. For e.g., you can call
the `.get_revisions()` method like so:

/// tab | Synchronous

```python
import anaplan_sdk

anaplan = anaplan_sdk.Client(
    workspace_id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    model_id="11111111111111111111111111111111",
    certificate="~/certs/anaplan.pem",
    private_key="~/keys/anaplan.pem",
)
lists = anaplan.alm.get_revisions()
```

///
/// tab | Asynchronous

```python
import anaplan_sdk

anaplan = anaplan_sdk.AsyncClient(
    workspace_id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    model_id="11111111111111111111111111111111",
    certificate="~/certs/anaplan.pem",
    private_key="~/keys/anaplan.pem",
)
lists = await anaplan.alm.get_revisions()

```

///

For brevity, if you need to access only the ALM API or need to do so repeatedly, you can assign the
ALM Client to it's own variable.

/// tab | Synchronous

```python
anaplan = anaplan_sdk.Client(
    workspace_id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    model_id="11111111111111111111111111111111",
    certificate="~/certs/anaplan.pem",
    private_key="~/keys/anaplan.pem",
)
alm = anaplan.alm
revisions = alm.get_revisions()
syncs = alm.get_sync_tasks()
```

///
/// tab | Asynchronous

```python
import asyncio

anaplan = anaplan_sdk.AsyncClient(
    workspace_id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    model_id="11111111111111111111111111111111",
    certificate="~/certs/anaplan.pem",
    private_key="~/keys/anaplan.pem",
)
alm = anaplan.alm
revisions, syncs = await asyncio.gather(alm.get_revisions(), alm.get_sync_tasks())
```

///

## Basic Usage

### Sync a revision from a source model to a target model

Configure your client with a model where you want to run the ALM model
sync.  This will be your target model that will be updated by the
model sync.  The following code will detect the latest revision and
use that as the target revision.  The first model in the target
revision's models will be where the revision was created.  This will
be your source model.  In a typical ALM setup this will be the
development model in standard mode where the changes are configured.
For this example, we will sync the first available change in the
source model.  This will be your source revision.

When the code completes, both models will share the source revision as
their latest revision.  The structural changes from the source model
will have been copied to the target model to match the source model
when the source revision was created.

/// tab | Synchronous
```python
from anaplan_sdk import Client

target_revision = anaplan.alm.get_latest_revision()
models = anaplan.alm.get_models_for_revision (target_revision.id)
source_model = models[0]
syncable_revisions = anaplan.alm.get_syncable_revisions (source_model.id)
source_revision = syncable_revisions[-1]
task_status = anaplan.alm.run_sync (source_model.id, source_revision.id, target_revision.id)

```

///
/// tab | Asynchronous
```python
from anaplan_sdk import AsyncClient

target_revision = await anaplan.alm.get_latest_revision()
models = await anaplan.alm.get_models_for_revision (target_revision.id)
source_model = models[0]
syncable_revisions = await anaplan.alm.get_syncable_revisions (source_model.id)
source_revision = syncable_revisions[-1]
task_status = await anaplan.alm.run_sync (source_model.id, source_revision.id, target_revision.id)

```

///


!!! note
      While you can instantiate a [Client](../api/client.md) without the workspace or model parameters, trying to access
      the [Transactional Client](../api/transactional_client.md) on an instance without the `model_id` will raise a `ValueError`.
