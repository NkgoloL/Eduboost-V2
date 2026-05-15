.................................................ss..................... [  4%]
........................................................................ [  9%]
........s............................................................... [ 14%]
........................................................................ [ 19%]
..........................ssssssssss.................................... [ 24%]
........................................................................ [ 29%]
........................................................................ [ 34%]
........................................................................ [ 39%]
........................................................................ [ 44%]
........................................................................ [ 49%]
........................................................................ [ 54%]
........................................................................ [ 59%]
........................................................................ [ 64%]
........................................................................ [ 69%]
........................................................................ [ 73%]
........................................................................ [ 78%]
........................................................................ [ 83%]
........................................................................ [ 88%]
........................................................................ [ 93%]
........................................................................ [ 98%]
....................                                                     [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/pydantic/_internal/_fields.py:160
  /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/lib/python3.12/site-packages/pydantic/_internal/_fields.py:160: UserWarning: Field "model_version" has conflict with protected namespace "model_".
  
  You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
    warnings.warn(

tests/unit/test_v2_repositories_full.py::TestLessonRepository::test_create_commits
  /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/repositories/lesson_repository.py:31: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    db.add(lesson)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_v2_repositories_full.py::TestDiagnosticRepository::test_create_session_commits
  /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app/core/base.py:52: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    db.add(instance)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/unit/test_v2_services_full.py::TestLessonServiceV2::test_get_lesson_from_redis
  /usr/lib/python3.12/unittest/mock.py:2188: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    def __init__(self, name, parent):
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1447 passed, 13 skipped, 4 warnings in 147.60s (0:02:27)
