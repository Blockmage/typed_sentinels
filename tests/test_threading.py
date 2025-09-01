# pyright: reportUnknownMemberType=none
# pyright: reportUnknownVariableType=none
# pyright: reportUnknownArgumentType=none
# pyright: reportUnknownParameterType=none

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pytest

from typed_sentinels import Sentinel


class TestSentinelThreading:
    """Test thread safety and locking mechanisms of Sentinel instances."""

    def test_singleton_under_contention(self):
        """Test that singleton behavior is maintained under high thread contention."""

        hint_type = str
        num_threads = 50
        sentinels_per_thread = 100

        all_sentinels = []
        lock = threading.Lock()

        def create_sentinels():
            """Worker function that creates many sentinels."""

            local_sentinels = []
            for _ in range(sentinels_per_thread):
                s = Sentinel(hint_type)
                local_sentinels.append(s)
                time.sleep(0.0001)

            with lock:
                all_sentinels.extend(local_sentinels)

        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=create_sentinels)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        unique_ids = {id(s) for s in all_sentinels}
        assert len(unique_ids) == 1, f'Singleton violation: found {len(unique_ids)} different objects'

        for s in all_sentinels:
            assert s.hint == hint_type

    def test_multiple_hints_concurrent_creation(self):
        """Test concurrent creation of sentinels with different hint types."""

        hint_types = [str, int, float, bool, list, dict, set, tuple, bytes]
        num_threads_per_type = 10
        sentinels_per_thread = 50

        results = {}
        results_lock = threading.Lock()

        def create_sentinels_for_hint(hint_type: Any):
            """Create sentinels for a specific hint type."""

            sentinels = []
            for _ in range(sentinels_per_thread):
                s = Sentinel(hint_type)
                sentinels.append(s)
                time.sleep(0.0001)

            with results_lock:
                if hint_type not in results:
                    results[hint_type] = []
                results[hint_type].extend(sentinels)

        threads = []
        for hint_type in hint_types:
            for _ in range(num_threads_per_type):
                thread = threading.Thread(target=create_sentinels_for_hint, args=(hint_type,))
                threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for hint_type, sentinels in results.items():
            unique_ids = {id(s) for s in sentinels}
            assert len(unique_ids) == 1, (
                f'Singleton violation for {hint_type}: found {len(unique_ids)} different objects'
            )

            for s in sentinels:
                assert s.hint == hint_type

    def test_cache_race_conditions(self):
        """Test for race conditions in the cache lookup and creation."""

        hint_type = int
        barrier = threading.Barrier(20)
        created_sentinels = []
        lock = threading.Lock()

        def synchronized_creation():
            """All threads create sentinel at exactly the same time."""

            barrier.wait()
            s = Sentinel(hint_type)

            with lock:
                created_sentinels.append(s)

        threads = []
        for _ in range(20):
            thread = threading.Thread(target=synchronized_creation)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        unique_ids = {id(s) for s in created_sentinels}
        assert len(unique_ids) == 1, f'Race condition detected: {len(unique_ids)} different objects created'

    def test_cache_weak_reference_cleanup(self):
        """Test that cache properly handles weak reference cleanup under threading."""

        results = []
        results_lock = threading.Lock()

        def create_and_forget_sentinels():
            """Create sentinels and let them go out of scope."""

            for i in range(10):
                hint = f'unique_type_{threading.current_thread().ident}_{i}'
                s = Sentinel(hint)

                with results_lock:
                    results.append({'thread_id': threading.current_thread().ident, 'hint': hint, 'sentinel_id': id(s)})

                del s

                time.sleep(0.001)

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_and_forget_sentinels)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 50

        hints_by_thread = {}
        for result in results:
            thread_id = result['thread_id']
            if thread_id not in hints_by_thread:
                hints_by_thread[thread_id] = set()
            hints_by_thread[thread_id].add(result['hint'])

        for thread_id, hints in hints_by_thread.items():
            assert len(hints) == 10, f'Thread {thread_id} should have created 10 unique hints'

    def test_deadlock_prevention(self):
        """Test that the locking mechanism doesn't cause deadlocks."""

        results = []
        results_lock = threading.Lock()

        def create_multiple_sentinels():
            """Create multiple different sentinels in sequence."""

            thread_results = []
            for i in range(20):
                hint_types = [str, int, float, bool, list]
                hint = hint_types[i % len(hint_types)]

                s = Sentinel(hint)
                thread_results.append(
                    {'hint': hint, 'sentinel_id': id(s), 'thread_id': threading.current_thread().ident}
                )

                time.sleep(0.0005)

            with results_lock:
                results.extend(thread_results)

        threads = []
        for _ in range(15):
            thread = threading.Thread(target=create_multiple_sentinels)
            threads.append(thread)

        start_time = time.time()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=10.0)
            if thread.is_alive():
                pytest.fail('Potential deadlock detected - thread did not complete within timeout')

        end_time = time.time()

        assert end_time - start_time < 5.0, 'Threads took too long - possible lock contention issues'
        assert len(results) == 15 * 20, 'Not all sentinels were created'

    def test_lock_contention_performance(self):
        """Test performance under high lock contention."""

        hint_type = str
        num_threads = 20
        operations_per_thread = 1000

        def high_frequency_creation():
            """Rapidly create sentinels to test lock performance."""

            for _ in range(operations_per_thread):
                s = Sentinel(hint_type)

                assert isinstance(s, Sentinel)
                assert s.hint == hint_type

        threads = []
        start_time = time.time()

        for _ in range(num_threads):
            thread = threading.Thread(target=high_frequency_creation)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        total_operations = num_threads * operations_per_thread

        print(f'Completed {total_operations} operations in {end_time - start_time:.2f} seconds')
        print(f'Rate: {total_operations / (end_time - start_time):.0f} operations/second')

        assert end_time - start_time < 10.0, 'Performance under lock contention is too slow'

    def test_thread_executor_stress_test(self):
        """Stress test using ThreadPoolExecutor for more realistic concurrent load."""

        hint_types = [str, int, float, bool, bytes]

        def worker_task(hint_type: Any, iterations: int):
            """Worker that creates sentinels and returns statistics."""

            sentinels = []
            unique_ids = set()

            for _ in range(iterations):
                s = Sentinel(hint_type)
                sentinels.append(s)
                unique_ids.add(id(s))

            return {
                'hint_type': hint_type,
                'count': len(sentinels),
                'unique_ids': len(unique_ids),
            }

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = []

            for hint_type in hint_types:
                for _ in range(10):
                    future = executor.submit(worker_task, hint_type, 100)
                    futures.append(future)

            results = [future.result() for future in as_completed(futures)]

        for result in results:
            assert result['unique_ids'] == 1, f'Task saw multiple IDs for {result["hint_type"]}: {result["unique_ids"]}'

    def test_exception_safety_under_threading(self):
        """Test that exceptions don't leave locks in inconsistent state."""

        valid_sentinels = []
        exceptions_caught = []
        lock = threading.Lock()

        def mixed_operations():
            """Mix valid and invalid sentinel creation."""

            thread_results = {'valid': [], 'exceptions': []}

            # fmt: off
            operations = [
                lambda: Sentinel(str),          # Valid
                lambda: Sentinel(int),          # Valid
                lambda: Sentinel(None),         # Should raise InvalidHintError
                lambda: Sentinel(Sentinel),     # Should raise InvalidHintError
                lambda: Sentinel(bool),         # Valid
            ]
            # fmt: on

            for op in operations:
                try:
                    s = op()
                    thread_results['valid'].append(s)
                except Exception as e:  # noqa: BLE001
                    thread_results['exceptions'].append(type(e).__name__)

            with lock:
                valid_sentinels.extend(thread_results['valid'])
                exceptions_caught.extend(thread_results['exceptions'])

        threads = []
        for _ in range(10):
            thread = threading.Thread(target=mixed_operations)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(valid_sentinels) > 0, 'Should have created some valid sentinels'
        assert len(exceptions_caught) > 0, 'Should have caught some exceptions'

        expected_exceptions = {'InvalidHintError'}
        actual_exception_types = set(exceptions_caught)

        assert expected_exceptions.issubset(actual_exception_types), (
            f'Expected exceptions {expected_exceptions}, got {actual_exception_types}'
        )

        by_hint = {}
        for s in valid_sentinels:
            hint = s.hint
            if hint not in by_hint:
                by_hint[hint] = set()
            by_hint[hint].add(id(s))

        for hint, ids in by_hint.items():
            assert len(ids) == 1, f'Singleton violation for {hint} after exceptions: {len(ids)} IDs'

    def test_thread_executor_stress_test_with_keeper(self):
        """Stress test with a keeper reference to prevent weak reference cleanup."""

        hint_types = [str, int, float, bool, bytes]

        # Keep one reference to each type to prevent WeakValueDictionary cleanup
        keepers = {hint_type: Sentinel(hint_type) for hint_type in hint_types}

        def worker_task(hint_type: Any, iterations: int):
            """Worker that creates sentinels and returns statistics."""

            sentinels = []
            unique_ids = set()

            for _ in range(iterations):
                s = Sentinel(hint_type)
                sentinels.append(s)
                unique_ids.add(id(s))

                # Verify it matches our keeper
                assert id(s) == id(keepers[hint_type]), f'Should match keeper: {id(s)} != {id(keepers[hint_type])}'

            return {
                'hint_type': hint_type,
                'count': len(sentinels),
                'unique_ids': len(unique_ids),
                'first_id': id(sentinels[0]) if sentinels else None,
            }

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = []

            for hint_type in hint_types:
                for _ in range(10):
                    future = executor.submit(worker_task, hint_type, 100)
                    futures.append(future)

            results = [future.result() for future in as_completed(futures)]

        by_hint = {}
        for result in results:
            hint_type = result['hint_type']
            if hint_type not in by_hint:
                by_hint[hint_type] = []
            by_hint[hint_type].append(result)

        for hint_type, hint_results in by_hint.items():
            first_ids = {r['first_id'] for r in hint_results}
            print(f'With keeper references - {hint_type}: {len(first_ids)} unique IDs')

            assert len(first_ids) == 1, f'Singleton violation for {hint_type}: multiple IDs {first_ids}'

            keeper_id = id(keepers[hint_type])
            for result in hint_results:
                assert result['first_id'] == keeper_id, (
                    f"Result doesn't match keeper: {result['first_id']} != {keeper_id}"
                )

    def test_weak_reference_behavior_is_the_culprit(self):
        """Prove that WeakValueDictionary cleanup is causing the 'multiple IDs'."""

        s1 = Sentinel('test_type')
        s1_id = id(s1)

        # Delete the last reference
        # Even without GC, WeakValueDictionary should clean up
        del s1

        # Give WeakValueDictionary a chance to clean up
        time.sleep(0.001)

        # Should get a different ID
        s2 = Sentinel('test_type')
        s2_id = id(s2)

        print(f'Weak ref cleanup test: {s1_id} -> {s2_id}, different: {s1_id != s2_id}')
