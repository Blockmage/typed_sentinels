import gc
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from typed_sentinels import Sentinel


def create_sentinel_worker(
    thread_id: int, sentinel_type: Any, iterations: int = 100
) -> tuple[int, int, list[Sentinel]]:
    """Create `Sentinel` instances in a tight loop."""

    local_instances: list[Sentinel] = []
    local_instance_ids: set[int] = set()

    for i in range(iterations):
        s = Sentinel(sentinel_type)
        local_instances.append(s)
        local_instance_ids.add(id(s))

        if i % 20 == 0 and local_instances:
            local_instances.pop(0)

    return thread_id, len(local_instance_ids), local_instances


def run_1() -> None:
    print('=== Test 1: Multiple threads creating Sentinel(str) ===')

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_sentinel_worker, i, str, 50) for i in range(10)]

        all_instances: list[Sentinel] = []
        results: list[tuple[int, int]] = []

        for future in as_completed(futures):
            thread_id, unique_ids, instances = future.result()
            results.append((thread_id, unique_ids))
            all_instances.extend(instances)

        print(f'Cache size during concurrent creation: {len(Sentinel._cls_cache)}')
        print(f'All instances are identical: {len({id(inst) for inst in all_instances}) == 1}')

        for thread_id, unique_ids in sorted(results):
            print(f'Thread {thread_id}: saw {unique_ids} unique instance ID(s)')


def run_2() -> None:
    print('\n=== Test 2: Multiple threads with different types ===')

    types_to_test = [str, int, list, dict, set, complex, range, dict[str, str], tuple[bytes, ...], Callable[..., Any]]

    with ThreadPoolExecutor(max_workers=len(types_to_test)) as executor:
        futures = [executor.submit(create_sentinel_worker, i, typ, 30) for i, typ in enumerate(types_to_test)]

        type_results: dict[Any, tuple[int, list[Sentinel]]] = {}

        for future in as_completed(futures):
            thread_id, unique_ids, instances = future.result()
            typ = types_to_test[thread_id]
            type_results[typ] = (unique_ids, instances)

        print(f'Cache size with {len(types_to_test)} types: {len(Sentinel._cls_cache)}')

        for typ, (unique_ids, instances) in type_results.items():
            all_ids_for_type = {id(inst) for inst in instances}
            print(f'{typ.__name__}: {len(all_ids_for_type)} unique instance(s), saw {unique_ids} unique ID(s)')


def run_3() -> None:
    print('\n=== Test 3: Concurrent creation and deletion ===')

    def create_and_delete_worker(iterations: int = 50):
        for i in range(iterations):
            Sentinel(str)
            if i % 10 == 0:
                gc.collect()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_and_delete_worker, 100) for _ in range(5)]
        for future in as_completed(futures):
            future.result()

    print(f'Cache size after concurrent create/delete: {len(Sentinel._cls_cache)}')


def cleanup() -> None:
    gc.collect()
    print(f'Final cache size after cleanup: {len(Sentinel._cls_cache)}')


if __name__ == '__main__':
    run_1()
    run_2()
    run_3()
    cleanup()
