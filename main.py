import argparse
import json
import os
import sys
import requests

prog = "Google Suggestions"
description = "This program produces Google auto-complete suggestions of provided keywords"
key_help = "A list of keywords separated by spaces to get Google Suggestions for"
key_file_help = "A text file of keywords separated by commas to get Google Suggestions for"
out_file_help = "A json file of the Google Suggestions results (default is ./output.json)"
default_output_file = os.path.join(os.getcwd(), "output.json")

parser = argparse.ArgumentParser(prog=prog, description=description)
parser.add_argument("-k", "--keywords", required=False,
                    nargs="*", help=key_help)
parser.add_argument("-f", "--filename", required=False,
                    nargs=1, help=key_file_help)
parser.add_argument("-o", "--output", required=False,
                    nargs=1, help=out_file_help)


def load_keyword_file(key_path: str):
    keywords = []
    if len(key_path) < 1 and os.path.isfile(key_path) is False:
        return keywords
    else:
        with open(key_path, "r+") as keyword_file:
            lines = [line.strip().split(",")
                     for line in keyword_file.readlines()]
            keywords = [
                keyword.strip() for row in lines for keyword in row if len(keyword) > 1
            ]
    return keywords


def get_all_keywords(direct_keys: [str], key_file_dir: str):
    keywords = []
    if direct_keys is None or len(direct_keys) < 1:
        parser.print_help()
        sys.exit(1)
    loaded_file_keywords = load_keyword_file(key_file_dir)
    keywords.extend(direct_keys)
    keywords.extend(loaded_file_keywords)
    return keywords


def parse_args():
    args = parser.parse_args()
    keyword_args = args.keywords
    keyword_file_arg = args.filename[0] if args.filename else ""
    output_file_arg = args.output[0] if args.output else default_output_file

    if keyword_args is None and keyword_file_arg is None:
        parser.print_help()
        sys.exit(1)

    return {
        "keywords": keyword_args,
        "keywords_file": keyword_file_arg,
        "output_file": os.path.join(os.getcwd(), f"{output_file_arg}"),
    }


if __name__ == "__main__":
    args = parse_args()
    keywords = args.get("keywords")
    keywords_file = args.get("keywords_file")
    output_file = args.get("output_file")
    all_keywords = get_all_keywords(
        args.get("keywords"), args.get("keywords_file"))
    results = {}
    suggestions_url = "https://www.google.com/complete/search?client=chrome&q="
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"
    }

    for keyword in all_keywords:
        url = f"{suggestions_url}{keyword}"
        response = requests.get(url, headers=headers)
        parsed_response = json.loads(response.text)[1]
        results[keyword] = parsed_response

    with open(output_file, "w+") as output:
        output.write(json.dumps(results, indent=4))
