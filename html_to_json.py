import os
import json
from bs4 import BeautifulSoup, NavigableString

INPUT_PATH = "manual_input/html_in.txt"
OUTPUT_PATH = "transformed/output.json"


def node_to_dict(node):
    if isinstance(node, NavigableString):
        text = str(node)
        if not text.strip():
            return None
        return {"type": "text", "text": text}

    if not hasattr(node, "name"):
        return None

    data = {
        "type": "element",
        "tag": node.name,
    }

    ui = node.attrs.pop("data-ui", None)
    if ui is not None:
        data["ui"] = ui

    if node.attrs:
        data["attrs"] = node.attrs

    children = []
    for child in node.children:
        child_dict = node_to_dict(child)
        if child_dict is not None:
            children.append(child_dict)
    if children:
        data["children"] = children

    return data


def transform_html_to_json(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    root = soup.body if soup.body is not None else soup

    result = []
    for child in root.children:
        d = node_to_dict(child)
        if d is not None:
            result.append(d)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    transform_html_to_json(INPUT_PATH, OUTPUT_PATH)

