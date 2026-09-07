from jobforge import Queue

def test_lifecycle_and_retry(tmp_path):
    q = Queue(tmp_path / "jobs.db")
    job_id = q.enqueue("build:42")
    job = q.claim()
    assert job and job.id == job_id and job.attempts == 1
    q.fail(job_id)
    retry = q.claim()
    assert retry and retry.attempts == 2
    q.complete(job_id)
    assert q.stats()["done"] == 1

def test_dead_letter_after_max_attempts(tmp_path):
    q = Queue(tmp_path / "jobs.db")
    job_id = q.enqueue("unstable")
    for _ in range(3):
        assert q.claim() is not None
        q.fail(job_id, max_attempts=3)
    assert q.claim() is None
    assert q.stats()["dead"] == 1
