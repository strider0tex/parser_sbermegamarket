import unittest
from unittest.mock import MagicMock, patch
from scraper import ProductScraper  # Импортируем класс из основного скрипта


class TestProductScraper(unittest.TestCase):

    @patch('selenium.webdriver.Chrome')
    def setUp(self, MockWebDriver):
        self.mock_driver = MockWebDriver()
        self.scraper = ProductScraper(self.mock_driver, "http://example.com/product")

    def test_extract_product_image(self):
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "http://example.com/image.jpg"
        self.scraper.get_element = MagicMock(return_value=mock_element)

        result = self.scraper.extract_product_image()
        self.assertEqual(result, "http://example.com/image.jpg")

    def test_extract_product_name(self):
        mock_element = MagicMock()
        mock_element.text = "Название продукта"
        self.scraper.get_element = MagicMock(return_value=mock_element)

        result = self.scraper.extract_product_name()
        self.assertEqual(result, "Название продукта")

    def test_extract_product_price(self):
        mock_element = MagicMock()
        mock_element.text = "1000"
        self.scraper.get_element = MagicMock(return_value=mock_element)

        result = self.scraper.extract_product_price()
        self.assertEqual(result, "1000")


if __name__ == '__main__':
    unittest.main()
