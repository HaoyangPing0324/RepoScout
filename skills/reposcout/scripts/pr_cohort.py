"""Calculate comparable PR statistics from a complete, read-only GitHub snapshot."""

import argparse
import hashlib
import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

EXTERNAL = {"NONE", "CONTRIBUTOR", "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR"}
INTERNAL = {"OWNER", "MEMBER", "COLLABORATOR", "MANNEQUIN"}
REVIEWED = {"APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED"}


def instant(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamps need an explicit UTC offset.")
    return dt.astimezone(timezone.utc)


def window(as_of, zone):
    # Choose the latest local Monday midnight whose last cohort member has 336h follow-up.
    matured = (as_of - timedelta(days=14)).astimezone(zone).date()
    end = matured - timedelta(days=matured.weekday())
    return tuple(datetime.combine(date, time.min, zone) for date in (end - timedelta(days=7), end))


def is_bot(user):
    return user["type"] == "Bot" or user["login"].lower().endswith("[bot]")


def hours(delta):
    return delta.total_seconds() / 3600


def analyze(data, sample_only):
    cutoff = instant(data["as_of"])
    start, end = window(cutoff, ZoneInfo(data["timezone"]))
    if not data["cohort_complete"]:
        raise ValueError("Cohort incomplete. Report the affected metrics as 数据缺失.")
    eligible = {}
    for pr in data["pulls"]:
        if not start <= instant(pr["created_at"]) < end:
            continue
        if pr["excluded_reason"] or (pr["user"] and is_bot(pr["user"])):
            continue
        association = pr["author_association"]
        if association in INTERNAL:
            continue
        if association not in EXTERNAL or not pr["user"]:
            raise ValueError("Unknown author or association. Resolve or mark cohort incomplete.")
        number = pr["number"]
        if number in eligible:
            raise ValueError(f"Duplicate PR #{number}. Deduplicate the input snapshot.")
        eligible[number] = pr

    seed = f'{data["repo"].lower()}|{start.date()}|'
    sample = sorted(eligible, key=lambda n: (hashlib.sha256(f"{seed}{n}".encode()).digest(), n))[:12]
    result = {"window": [start.isoformat(), end.isoformat()], "seed_prefix": seed, "sample": sample}
    if sample_only:
        return result

    merged_hours = []
    for pr in eligible.values():
        merged_at = pr["merged_at"]
        if merged_at and instant(merged_at) <= cutoff:
            elapsed = hours(instant(merged_at) - instant(pr["created_at"]))
            if elapsed < 0:
                raise ValueError("Merge precedes PR creation.")
            merged_hours.append(elapsed)
    result.update(external=len(eligible), merged_by_14d=sum(h <= 336 for h in merged_hours),
                  merged_by_cutoff=len(merged_hours),
                  median_merge_hours=median(merged_hours) if merged_hours else None)

    waits = []
    observations = []
    for number in sample:
        pr = eligible[number]
        reviews = data.get("reviews", {}).get(str(number))
        observation = {"number": number, "status": "数据缺失"}
        if reviews is not None:
            submitted = []
            ambiguous = []
            unknown_time = False
            for review in reviews:
                if review["state"] not in REVIEWED:
                    continue
                actor = review["user"]
                if actor and (is_bot(actor) or actor["login"].lower() == pr["user"]["login"].lower()):
                    continue
                if not review["submitted_at"]:
                    unknown_time = True
                    continue
                when = instant(review["submitted_at"])
                if when > cutoff:
                    continue
                if actor is None:
                    ambiguous.append(when)
                else:
                    submitted.append(when)
            first = min(submitted, default=None)
            uncertain = unknown_time or any(first is None or when < first for when in ambiguous)
            if uncertain:
                observations.append(observation)
                continue
            if first is None:
                observation["status"] = "未见首评"
            else:
                wait = hours(first - instant(pr["created_at"]))
                if wait < 0:
                    raise ValueError("Review precedes PR creation.")
                waits.append(wait)
                observation.update(status="有首评", hours=wait, first_review=first.isoformat())
        observations.append(observation)
    result.update(reviewed=len(waits), review_missing=sum(o["status"] == "数据缺失" for o in observations),
                  median_review_hours=median(waits) if waits else None, observations=observations)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--sample-only", action="store_true", help="Select PRs before retrieving reviews.")
    args = parser.parse_args()
    print(json.dumps(analyze(json.loads(args.snapshot.read_text()), args.sample_only),
                     ensure_ascii=False, indent=2))
