# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup
# pyrefly: ignore [missing-import]
import logfire

def parse_html(file_path : str):
    """
    pareses HTML content using BeautifulSoup.
    clean scripts, styles, and readable text for RAG.
    """
    with logfire.span("HTML Parsing", filename = file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors= "ignore") as f:
                content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            # 1. remove junk
            for script in soup(["script","style","meta","noscript"]):
                script.decompose()
            # 2. Extract text
            text = soup.get_text(separator = "\n")
            # 3. Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split(' '))
            text_clean = '\n'.join(chunk for chunk in chunks if chunk)
            logfire.info("HTML Parsed")
            return text_clean
        except Exception as e:
            logfire.error(f"❌ HTML Parse Failed: {e}")
            raise e
            

                
    
