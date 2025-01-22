# Usage
1.    Create a `config.json` file in the same directory as the `main.py` file.
It should have the same format as in the [example below](#configjson-example).
2.   Place your images inside the folder you provided as `"img_dir"`.
3.   Run main.py.


# config.json example
```json
{
    "group_id": <group_id>,
    "token": "<your_access_token>",
    "shuffle": 1,
    "sort_descend": 0,
    "start": {
        "hour": 8,
        "minute": 30
    },
    "end": {
        "hour": 0,
        "minute": 30
    },
    "step": {
        "hour": 3,
        "minute": 0
    },
    "img_dir": "./img",
    "done_dir": "./done"
}
```
