import functools
import inspect

import diskcache
from pydantic import BaseModel

cache = diskcache.Cache("../cache")


def instructor_cache(func):
    """Cache a function that returns a Pydantic model"""
    return_type = inspect.signature(func).return_annotation  #
    if not issubclass(return_type, BaseModel):  #
        raise ValueError("The return type must be a Pydantic model")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = f"{func.__name__}-{functools._make_key(args, kwargs, typed=False)}"  #
        # Check if the result is already cached
        if (cached := cache.get(key)) is not None:
            # Deserialize from JSON based on the return type
            return return_type.model_validate_json(cached) # type: ignore

        # Call the function and cache its result
        result = func(*args, **kwargs)
        serialized_result = result.model_dump_json()
        cache.set(key, serialized_result)

        return result

    return wrapper
