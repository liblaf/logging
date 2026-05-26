from __future__ import annotations

import logging

import limits
import pytest

from liblaf.logging.filters import LimitOptions, LimitsFilter


def make_record(limits: object = None, *, lineno: int = 10) -> logging.LogRecord:
    record = logging.LogRecord(
        "liblaf.logging.tests",
        logging.INFO,
        __file__,
        lineno,
        "hello",
        (),
        None,
    )
    if limits is not None:
        record.limits = limits
    return record


def test_records_without_limits_are_not_filtered() -> None:
    assert LimitsFilter().filter(make_record()) is True


def test_none_limit_option_is_not_filtered() -> None:
    record = make_record(LimitOptions(item=None))

    assert LimitsFilter().filter(record) is True


def test_string_limit_suppresses_repeated_record() -> None:
    limiter = LimitsFilter()
    record = make_record("1/minute")

    assert limiter.filter(record) is True
    assert limiter.filter(record) is False


def test_rate_limit_item_is_accepted_directly() -> None:
    limiter = LimitsFilter()
    record = make_record(limits.parse("1/minute"))

    assert limiter.filter(record) is True
    assert limiter.filter(record) is False


def test_limit_options_can_share_namespace_and_charge_cost() -> None:
    limiter = LimitsFilter()
    options = LimitOptions(
        "2/minute",
        namespace=("shared",),
        identifiers=("operation",),
        cost=2,
    )

    assert limiter.filter(make_record(options, lineno=10)) is True
    assert limiter.filter(make_record(options, lineno=11)) is False


def test_default_namespace_keeps_different_call_sites_independent() -> None:
    limiter = LimitsFilter()

    assert limiter.filter(make_record("1/minute", lineno=10)) is True
    assert limiter.filter(make_record("1/minute", lineno=11)) is True


def test_invalid_limits_argument_raises_value_error() -> None:
    with pytest.raises(ValueError, match="123"):
        LimitsFilter().filter(make_record(123))


def test_invalid_limit_option_item_raises_value_error() -> None:
    with pytest.raises(ValueError, match="object"):
        LimitOptions(object())
