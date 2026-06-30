# Database Migration Latest Run

**Status:** migration evidence failed
<!-- Status: migration evidence failed -->

- Captured at: `2026-05-16T20:09:41Z`
- Database URL: `postgresql+asyncpg://real_user:***@localhost:5432/eduboost_test`
- Include downgrade: `False`
- JSON evidence: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/migration_latest.json`

| Step | Command | Return code | Passed |
|---|---|---:|---|
| alembic_current_before | `alembic current` | 1 | no |
| alembic_upgrade_head | `alembic upgrade head` | 1 | no |
| alembic_current_after | `alembic current` | 1 | no |
| migration_graph_check | `/usr/bin/python3 scripts/verify_migration_graph.py` | 0 | yes |
| schema_integrity_check | `/usr/bin/python3 scripts/validate_schema_integrity.py` | 0 | yes |

## Command output

### alembic_current_before

```text
Traceback (most recent call last):
  File "/home/nkgolol/.local/bin/alembic", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 641, in main
    CommandLine(prog=prog).main(argv=argv)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 631, in main
    self.run_cmd(cfg, options)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 608, in run_cmd
    fn(
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/command.py", line 625, in current
    script.run_env()
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/script/base.py", line 583, in run_env
    util.load_python_file(self.dir, "env.py")
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/util/pyfiles.py", line 95, in load_python_file
    module = load_module_py(module_id, path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/util/pyfiles.py", line 113, in load_module_py
    spec.loader.exec_module(module)  # type: ignore
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 90, in <module>
    run_migrations_online()
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 84, in run_migrations_online
    asyncio.run(run_async_migrations())
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 78, in run_async_migrations
    async with connectable.connect() as connection:
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/base.py", line 121, in __aenter__
    return await self.start(is_ctxmanager=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/engine.py", line 273, in start
    await greenlet_spawn(self.sync_engine.connect)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn
    result = context.throw(*sys.exc_info())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3276, in connect
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3300, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout
    rec = pool._do_get()
          ^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get
    return self._create_connection()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection
    return _ConnectionRecord(self)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__
    self.__connect()
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect
    with util.safe_reraise():
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect
    return dialect.connect(*cargs, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 620, in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 937, in connect
    await_only(creator_fn(*arg, **kw)),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 131, in await_only
    return current.driver.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connection.py", line 2329, in connect
    return await connect_utils._connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 991, in _connect
    conn = await _connect_addr(
           ^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 828, in _connect_addr
    return await __connect_addr(params, True, *args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 876, in __connect_addr
    await connected
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "real_user"
```

### alembic_upgrade_head

```text
Traceback (most recent call last):
  File "/home/nkgolol/.local/bin/alembic", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 641, in main
    CommandLine(prog=prog).main(argv=argv)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 631, in main
    self.run_cmd(cfg, options)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 608, in run_cmd
    fn(
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/command.py", line 403, in upgrade
    script.run_env()
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/script/base.py", line 583, in run_env
    util.load_python_file(self.dir, "env.py")
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/util/pyfiles.py", line 95, in load_python_file
    module = load_module_py(module_id, path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/util/pyfiles.py", line 113, in load_module_py
    spec.loader.exec_module(module)  # type: ignore
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 90, in <module>
    run_migrations_online()
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 84, in run_migrations_online
    asyncio.run(run_async_migrations())
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 78, in run_async_migrations
    async with connectable.connect() as connection:
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/base.py", line 121, in __aenter__
    return await self.start(is_ctxmanager=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/engine.py", line 273, in start
    await greenlet_spawn(self.sync_engine.connect)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn
    result = context.throw(*sys.exc_info())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3276, in connect
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3300, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout
    rec = pool._do_get()
          ^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get
    return self._create_connection()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection
    return _ConnectionRecord(self)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__
    self.__connect()
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect
    with util.safe_reraise():
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect
    return dialect.connect(*cargs, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 620, in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 937, in connect
    await_only(creator_fn(*arg, **kw)),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 131, in await_only
    return current.driver.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connection.py", line 2329, in connect
    return await connect_utils._connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 991, in _connect
    conn = await _connect_addr(
           ^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 828, in _connect_addr
    return await __connect_addr(params, True, *args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 876, in __connect_addr
    await connected
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "real_user"
```

### alembic_current_after

```text
Traceback (most recent call last):
  File "/home/nkgolol/.local/bin/alembic", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 641, in main
    CommandLine(prog=prog).main(argv=argv)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 631, in main
    self.run_cmd(cfg, options)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/config.py", line 608, in run_cmd
    fn(
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/command.py", line 625, in current
    script.run_env()
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/script/base.py", line 583, in run_env
    util.load_python_file(self.dir, "env.py")
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/util/pyfiles.py", line 95, in load_python_file
    module = load_module_py(module_id, path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/alembic/util/pyfiles.py", line 113, in load_module_py
    spec.loader.exec_module(module)  # type: ignore
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 90, in <module>
    run_migrations_online()
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 84, in run_migrations_online
    asyncio.run(run_async_migrations())
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/alembic/env.py", line 78, in run_async_migrations
    async with connectable.connect() as connection:
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/base.py", line 121, in __aenter__
    return await self.start(is_ctxmanager=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/engine.py", line 273, in start
    await greenlet_spawn(self.sync_engine.connect)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn
    result = context.throw(*sys.exc_info())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3276, in connect
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 146, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3300, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 449, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1263, in _checkout
    fairy = _ConnectionRecord.checkout(pool)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout
    rec = pool._do_get()
          ^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 308, in _do_get
    return self._create_connection()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 390, in _create_connection
    return _ConnectionRecord(self)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__
    self.__connect()
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect
    with util.safe_reraise():
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 643, in connect
    return dialect.connect(*cargs, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 620, in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 937, in connect
    await_only(creator_fn(*arg, **kw)),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 131, in await_only
    return current.driver.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connection.py", line 2329, in connect
    return await connect_utils._connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 991, in _connect
    conn = await _connect_addr(
           ^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 828, in _connect_addr
    return await __connect_addr(params, True, *args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/nkgolol/.local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 876, in __connect_addr
    await connected
asyncpg.exceptions.InvalidPasswordError: password authentication failed for user "real_user"
```

### migration_graph_check

```text
Migration graph OK: 21 revisions, head=20260516_0100
```

### schema_integrity_check

```text
Schema integrity OK
```
