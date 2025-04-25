import requests

NOTION_API_KEY = "secret_Xh3OQ4ASf9ZZEXldj0Hxgw8RHXC1MJOwVWz80fO6Xfl"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",  # Latest Notion API version
    "Content-Type": "application/json"
}


class NotionParser:
    def __init__(self):
        # Dispatch table: maps block types to handler methods
        self.handlers = {
            "bulleted_list_item": self.parse_text,
            "heading_1": self.parse_text,
            "heading_2": self.parse_text,
            "heading_3": self.parse_text,
            "callout": self.parse_text,
            "numbered_list_item": self.parse_text,
            "paragraph": self.parse_text,
            "quote": self.parse_text,
            
            "divider": self.parse_divider,

            "table": self.parse_table,
            
            "image": self.parse_image,
            
            "child_page": self.parse_child_page,

            "bookmark": self.parse_bookmark,

            "column_list": self.parse_column_list,

            "child_database": self.parse_child_database
        }

    def parse(self, block):
        """
        Main parser function that dispatches to the correct handler.

        :param block: A dictionary representing a Notion block.
        """
        block_type = block.get("type")
        assert block_type in self.handlers.keys(), f'Parsing of {block_type} not yet implemented'
        handler = self.handlers.get(block_type)
        return handler(block, block_type)

    def parse_divider(self, block, type=None):
        """Parses a divider."""
        return "---"
    
    def parse_bookmark(self, block,  type="bookmark"):
        print(block[type]["url"])

    def parse_image(self, block,  type="image"):
        """Parses an image."""
        img = block[type]
        try:
            return f"![Image]({img['external']['url']})"
        except:
            return f"![Image]({img['file']['url']})"

    def parse_text(self, block, type):
        """Parses a paragraph."""
        rich_text = block[type]['rich_text']
        if rich_text == []:
            return
        strings = [r["plain_text"] for r in rich_text]
        if type == 'bulleted_list_item':
            strings = ["- " + s for s in strings]
        formatted_string = " ".join(strings)  
        print(formatted_string) 


    def fetch_page_content(self, id):
        url = f"https://api.notion.com/v1/blocks/{id}/children"
        response = requests.get(url, headers=headers)
        data = response.json()
        return (data["results"])

    def parse_table(self, block,  type=None):
        table_id = block.get("id")
        table = self.fetch_page_content("0cfadcad-e646-423f-a4b0-536001a6878a") # get table names automatically ? 
        rows = [t["table_row"]["cells"] for t in table]
        table = ""
        for r in rows:
            row = []
            for c in r:
                row.append(c[0]["plain_text"])
            row = " | ".join(row)
            row += "\n"
            table += row
        print(table)

    def parse_child_page(self, block,  type=None):
        print("LOGIC FOR CHILD PAGE; TODO")
        # recursion to parse child page

    def parse_child_database(self, block,  type=None):
        print("LOGIC FOR CHILD DATABASE; TODO")
        # how to integrate context from column names ? 

    def parse_column_list(self, block,  type="column_list"):
        print(block[type])

