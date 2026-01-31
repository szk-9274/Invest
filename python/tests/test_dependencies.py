"""
TDD test for required dependencies

Issue: lxml is not installed in venv, causing ImportError
Solution: Add lxml to requirements.txt and verify it's importable
"""
import pytest


class TestRequiredDependencies:
    """Test that all required dependencies are installed"""

    def test_lxml_is_installed(self):
        """RED: lxml must be installed for pd.read_html() to work with flavor='lxml'"""
        try:
            import lxml
            import lxml.etree
            assert True, "lxml is installed"
        except ImportError as e:
            pytest.fail(f"lxml is not installed: {e}")

    def test_lxml_version(self):
        """GREEN: lxml should be a recent version"""
        import lxml
        # lxml should be version 4.0 or higher
        version = lxml.etree.LXML_VERSION
        assert version[0] >= 4, f"lxml version {version} is too old, need 4.0+"

    def test_pandas_can_use_lxml(self):
        """GREEN: pandas should be able to use lxml parser"""
        import pandas as pd
        # Create a simple HTML string
        html_string = """
        <table>
            <tr><th>Symbol</th><th>Name</th></tr>
            <tr><td>AAPL</td><td>Apple</td></tr>
            <tr><td>MSFT</td><td>Microsoft</td></tr>
        </table>
        """
        
        try:
            # This should work with lxml parser
            result = pd.read_html(html_string, flavor='lxml')
            assert len(result) == 1, "Should parse 1 table"
            assert len(result[0]) == 2, "Should have 2 rows"
            assert 'AAPL' in result[0]['Symbol'].values, "Should contain AAPL"
        except ImportError as e:
            pytest.fail(f"pandas cannot use lxml parser: {e}")


class TestHTMLParserAlternatives:
    """Test alternative HTML parsers if lxml fails"""

    def test_html5lib_available(self):
        """Verify html5lib is available as fallback"""
        try:
            import html5lib
            assert True
        except ImportError:
            pytest.skip("html5lib not installed (optional)")

    def test_beautifulsoup4_available(self):
        """Verify beautifulsoup4 is available as fallback"""
        try:
            import bs4
            assert True
        except ImportError:
            pytest.skip("beautifulsoup4 not installed (optional)")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
