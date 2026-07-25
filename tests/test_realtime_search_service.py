from app.models.nickname import NicknameCandidate
from app.services.realtime_search_service import RealtimeAvailabilityService


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0

    def search_character(self, server: str, nickname: str) -> list[dict[str, str]]:
        self.calls += 1
        return (
            []
            if server == "cain" and nickname == "검월"
            else [{"characterName": nickname}]
        )


def test_realtime_service_returns_only_available_results() -> None:
    client = FakeClient()
    service = RealtimeAvailabilityService(client, ["cain", "diregie"])  # type: ignore[arg-type]
    candidate = NicknameCandidate("검월", 0.9, 0.9, 0.9)

    results = service.check_candidate(candidate)

    assert len(results) == 1
    assert results[0].nickname == "검월"
    assert results[0].server == "cain"
    assert results[0].available is True


def test_realtime_service_caches_checked_nicknames() -> None:
    client = FakeClient()
    service = RealtimeAvailabilityService(client, ["cain"])  # type: ignore[arg-type]
    candidate = NicknameCandidate("검월", 0.9, 0.9, 0.9)

    assert service.check_candidate(candidate)
    assert service.check_candidate(candidate)

    assert client.calls == 1
    assert service.cache_size == 1
