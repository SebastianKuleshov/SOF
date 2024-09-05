import csv
from io import StringIO
from typing import List, Tuple, Any


async def generate_csv(
        sections: List[Tuple[str, List[str], List[List[Any]]]]
) -> str:
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)

    for title, headers, rows in sections:
        csv_writer.writerow([title])

        csv_writer.writerow(headers)

        for row in rows:
            csv_writer.writerow(row)

        csv_writer.writerow([])

    return csv_file.getvalue()
