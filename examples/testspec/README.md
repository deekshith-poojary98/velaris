# TestSpec IR Flow

Python authoring is the first adapter. The execution engine operates on `TestSpec` only.

```text
Python @test function
        │
        ▼
   collector.py          import module, find @test functions
        │
        ▼
   _CollectedTest        intermediate (Python-specific)
        │
        ▼
   validate_testspecs()   unique names, capabilities, callable
        │
        ▼
   TestSpec               format-agnostic IR
        │
        ▼
   runner.py              resolve → inject → spec.callable(**kwargs)
```

## Example

```python
# test_users.py
@test("api")
def test_users(api):
    ...
```

Becomes:

```python
TestSpec(
    name="test_users",
    capabilities=["api"],
    callable=test_users,
)
```

Future YAML or BDD adapters would produce the same `TestSpec` without changing the runner.
