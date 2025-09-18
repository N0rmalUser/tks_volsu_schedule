from app.database.schedule import Schedule


def snapshot():
    """Снимок текущего расписания: множество кортежей со всеми полями."""

    data = []
    for row in Schedule().get_all_schedule():
        data.append((
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7]
        ))
    return set(data)


def compare_snapshots(before, after):
    added = after - before
    removed = before - after

    return {
        "added": sorted(added),
        "removed": sorted(removed),
    }
