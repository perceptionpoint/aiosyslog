from datetime import datetime


def datetime2rfc3339(dt, is_utc=False):
    if is_utc is False:
        # calculating timezone
        d1 = datetime.now()
        d2 = datetime.utcnow()
        diff_hr = (d1 - d2).seconds / 60 / 60
        tz = ""

        if diff_hr == 0:
            tz = "Z"
        else:
            if diff_hr > 0:
                tz = "+%s" % (tz)

            tz = "%s%.2d%.2d" % (tz, diff_hr, 0)

        return "%s%s" % (dt.strftime("%Y-%m-%dT%H:%M:%S.%f"), tz)

    else:
        return dt.isoformat() + 'Z'
