#!/usr/bin/env python3

import argparse
import csv
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime


class JanusIssuesParser:
    def __init__(self, file_path: Optional[str] = None, html_content: Optional[str] = None):
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

        if not html_content:
            raise ValueError("You must provide either file_path or html_content")

        self.soup = BeautifulSoup(html_content, "lxml")
        self.rows = []

    # ----------------------------
    # Core parsing
    # ----------------------------
    def parse(self) -> List[List[str]]:
        results = []

        for tr in self.soup.find_all("tr"):
            tds = tr.find_all("td")
            if not tds:
                continue

            row = [
                td.get_text(separator=" ", strip=True)
                for td in tds
            ]

            results.append(row)

        self.rows = results
        return results

    # ----------------------------
    # Convert to dict
    # ----------------------------
    def to_dict(self, headers: Optional[List[str]] = None) -> List[Dict]:
        if not self.rows:
            self.parse()

        if not headers:
            headers = [
                "id",
                "rule",
                "start_time",
                "end_time",
                "link",
                "status",
                "details"
            ]

        return [dict(zip(headers, row)) for row in self.rows]

    # ----------------------------
    # Extract links
    # ----------------------------
    def extract_links(self) -> List[List[Optional[str]]]:
        links_data = []

        for tr in self.soup.find_all("tr"):
            row_links = []

            for td in tr.find_all("td"):
                a_tag = td.find("a")
                href = a_tag["href"] if a_tag and a_tag.has_attr("href") else None
                row_links.append(href)

            if row_links:
                links_data.append(row_links)

        return links_data

    # ----------------------------
    # Extract labels
    # ----------------------------
    def extract_labels(self) -> List[List[str]]:
        labels_data = []

        for tr in self.soup.find_all("tr"):
            row_labels = []

            for span in tr.find_all("span"):
                text = span.get_text(strip=True)
                if text:
                    row_labels.append(text)

            if row_labels:
                labels_data.append(row_labels)

        return labels_data

    # ----------------------------
    # Save CSV
    # ----------------------------
    def to_csv(self, output_path: str):
        if not self.rows:
            self.parse()

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(self.rows)

    # ----------------------------
    # Streaming (large files)
    # ----------------------------
    @staticmethod
    def stream_parse(file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            buffer = ""

            for line in f:
                buffer += line

                if "</tr>" in line:
                    soup = BeautifulSoup(buffer, "lxml")
                    tr = soup.find("tr")

                    if tr:
                        tds = tr.find_all("td")
                        row = [
                            td.get_text(separator=" ", strip=True)
                            for td in tds
                        ]
                        yield row

                    buffer = ""

    def summarize_events(self, output_path: str, delimiter: str = "|"):
        """
        Aggregate occurrences of 2nd column values and collect unique 1st column values.

        Output format:
        event_name, count, instances_list
        """

        if not self.rows:
            self.parse()

        summary = {}
        date_format = "%Y-%m-%d %H:%M:%S"  # for date parsing
        dates = []


        for row in self.rows:
            if len(row) < 2:
                continue

            col1 = row[0]  # first column (instance name)
            col2 = row[1]  # second column (event name)
            col3 = row[2]  # third column (issue date)

            if col2 not in summary:
                summary[col2] = {
                    "count": 0,
                    "unique_ids": set()
                }

            summary[col2]["count"] += 1
            summary[col2]["unique_ids"].add(col1)

            # for min and max date parsing
            if not col3:
                continue  #skip enmpty values

            try:
                date_obj = datetime.strptime(col3,date_format)
                dates.append(date_obj)
            except ValueError:
                continue

        # Write output file
        with open(output_path, "w", encoding="utf-8") as f:

            # add issues time line
            f.write(f"Generated with issues analyzed from '" + min(dates).strftime("%Y-%m-%d %H:%M:%S") + "' until '" + max(dates).strftime("%Y-%m-%d %H:%M:%S") + "'\n")

            # adding rest of data to file
            for event, data in summary.items():
                unique_ids_str = delimiter.join(sorted(data["unique_ids"]))
                line = f"{event},{data['count']},{unique_ids_str}\n"
                f.write(line)


        


# ----------------------------
# CLI ENTRY POINT
# ----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Parse Janus HTML issues into structured output"
    )

    parser.add_argument(
        "input_file",
        help="Path to input HTML file"
    )

    parser.add_argument(
        "-o", "--output",
        default="/output/output.csv",
        help="Output CSV file (default: /output/output.csv)"
    )

    parser.add_argument(
        "-s", "--summarize",
        default="/output/janus-summarize.csv",
        help="Sumarization CSV file (default: /output/janus-summarize.csv)"
    )

    parser.add_argument(
        "--links",
        action="store_true",
        help="Print extracted links"
    )

    parser.add_argument(
        "--labels",
        action="store_true",
        help="Print extracted labels"
    )

    args = parser.parse_args()

    parser_obj = JanusIssuesParser(file_path=args.input_file)

    # Always parse
    parser_obj.parse()

    # Save CSV
    parser_obj.to_csv(args.output)
    print(f"✅ CSV written to: {args.output}")

    # Optional outputs
    if args.links:
        print("\n🔗 Links:")
        for row in parser_obj.extract_links():
            print(row)

    if args.summarize:
        parser_obj.summarize_events(args.summarize)

    if args.labels:
        print("\n🏷 Labels:")
        for row in parser_obj.extract_labels():
            print(row)


if __name__ == "__main__":
    main()