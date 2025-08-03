import pytest
from app.services.text_extractor import TextExtractor

@pytest.fixture
def text_extractor():
    return TextExtractor()

class TestTextExtractor:
    @pytest.mark.asyncio
    async def test_extract_title(self, text_extractor):
        text = "Introduction\n\nThe Impact of Exercise on Health\n\nThis study examines..."
        title = text_extractor._extract_title(text)
        assert "The Impact of Exercise on Health" in title

    def test_parse_authors(self, text_extractor):
        author_string = "John Smith, Jane Doe; Robert Johnson"
        authors = text_extractor._parse_authors(author_string)
        assert len(authors) == 3
        assert "John Smith" in authors
        assert "Jane Doe" in authors
        assert "Robert Johnson" in authors

    def test_extract_abstract(self, text_extractor):
        text = """
        Title: Test Paper
        
        Abstract: This is the abstract of the paper. It contains important information
        about the study methodology and findings. The abstract should be extracted correctly.
        
        Introduction: This is the introduction section.
        """
        abstract = text_extractor._extract_abstract(text)
        assert "This is the abstract of the paper" in abstract

    def test_structure_content(self, text_extractor):
        messy_text = "This is   a   messy    text\n\n\n\nwith    extra    spaces\n\n\n"
        clean_text = text_extractor._structure_content(messy_text)
        assert "extra    spaces" not in clean_text
        assert "messy    text" not in clean_text