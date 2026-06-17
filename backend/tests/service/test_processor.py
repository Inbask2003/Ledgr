from app.service import processor


def test_charge_succeeds_when_rate_is_one(monkeypatch):
    monkeypatch.setattr(processor.settings, "processor_success_rate", 1.0)
    result = processor.charge()

    assert result.success is True
    assert result.failure_reason is None


def test_charge_fails_when_rate_is_zero(monkeypatch):
    monkeypatch.setattr(processor.settings, "processor_success_rate", 0.0)
    result = processor.charge()

    assert result.success is False
    assert result.failure_reason in processor.FAILURE_REASONS
