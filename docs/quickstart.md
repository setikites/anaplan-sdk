This Quickstart focuses on the Bulk APIs, which are the most commonly used APIs for data import and export. If you are
looking for different APIs, such as the Transactional APIs or CloudWork APIs, please refer to the respective 
[Guides](guides/index.md).

To get started, you can use basic authentication. Refer to the [Bulk API Guide](guides/bulk.md#instantiate-a-client) to
understand why this is not a good idea for production use.

??? info "Prerequisites"
    The Quickstart assumes you already have both valid credentials for your tenant, and the `workspace_id` and 
    `model_id` of the Model you want to work with. If you don't: You can find both of these either in the URL displayed 
    in the browser or by instantiating a client with Authentication information only and then calling the 
    `list_workspaces` and `list_models` methods. Alternatively, you can use an HTTP Client like Postman, Insomnia, 
    or Paw.

=== "Synchronous"
    ```python
    import anaplan_sdk
    
    anaplan = anaplan_sdk.Client(
        workspace_id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        model_id="11111111111111111111111111111111",
        user_email="admin@company.com",
        password="my_super_secret_password",
    )
    ```

=== "Asynchronous"
    ```python
    import anaplan_sdk
    
    anaplan = anaplan_sdk.AsyncClient(
        workspace_id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        model_id="11111111111111111111111111111111",
        user_email="admin@company.com",
        password="my_super_secret_password",
    )
    ```


## Importing Data

Start by listing available assets in your model. Typically, these will have already been created, and you will be
searching for a specific name provided by your Model Builder. Here, we will use one file and one process, which is
common practice.

=== "Synchronous"
    ```python
    file = anaplan.list_files()
    processes = anaplan.list_processes()
    ```

=== "Asynchronous"
    ```python
    from asyncio import gather
    
    files, processes = await gather(anaplan.list_files(), anaplan.list_processes())
    ```
??? info "Output"
    Models used in this Example: [File](api/models.md#anaplan_sdk.models.File), [Process](api/models.md#anaplan_sdk.models.Process).
    ```python
    [
        File(
            id=113000000000,
            name="Quickstart.csv",
            chunk_count=0,
            delimiter='"',
            encoding="UTF-8",
            first_data_row=2,
            format="txt",
            header_row=1,
            separator=",",
        )
    ]
    [Process(id=118000000000, name="Quickstart")]
    ```

With these two, you're ready to run your first import.

=== "Synchronous"
    ```python
    anaplan.upload_and_import(
        file_id=113000000000, action_id=118000000000, content=b"Hello, Anaplan!"
    )
    ```

=== "Asynchronous"
    ```python
    await anaplan.upload_and_import(
        file_id=113000000000, action_id=118000000000, content=b"Hello, Anaplan!"
    )
    ```
    
This will upload the file to Anaplan, trigger the process task, wait for the completion of the task and validate the task result. You can see the details of the task by inspecting the [TaskResult](api/models.md#anaplan_sdk.models.TaskResult).

## Exporting Data

Conversely, for exporting data, we start by listing the available exports.

=== "Synchronous"
    ```python
    exports = anaplan.list_exports()
    ```
=== "Asynchronous"
    ```python
    exports = await anaplan.list_exports()
    ```
??? info "Output"
    Models used in this Example: [Export](api/models.md#anaplan_sdk.models.Export).
    ```python
    [
        Export(
            id=116000000000,
            name="Quickstart Export",
            type="GRID_CURRENT_PAGE",
            format="text/csv",
            encoding="UTF-8",
            layout="GRID_CURRENT_PAGE",
        )
    ]
    ```

=== "Synchronous"
    ```python
    content = anaplan.export_and_download(116000000000)
    ```
=== "Asynchronous"
    ```python
    content = await anaplan.export_and_download(116000000000)
    ```

## Next Steps

To gain a better understanding of how Anaplan handles data, head over to the [Anaplan Explained](anaplan_explained.md)
section.

For a more detailed guide on how to use both the [Bulk APIs](guides/bulk.md)
and [Transactional APIs](guides/transactional.md), refer
to the Guides.
