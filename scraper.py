import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, driver):
        self.driver = driver

    def get_element(self, by, value, timeout=20):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            logger.error(f"Истекло время ожидания элемента по {by}: {value}")
        except NoSuchElementException:
            logger.error(f"Элемент не найден по {by}: {value}")
        return None

    def get_elements(self, by, value, timeout=20):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            logger.error(f"Истекло время ожидания элементов по {by}: {value}")
        except NoSuchElementException:
            logger.error(f"Элементы не найдены по {by}: {value}")
        return []

    def handle_exceptions(self, action):
        try:
            return action()
        except TimeoutException:
            logger.error("Истекло время ожидания элемента")
        except NoSuchElementException:
            logger.error("Элемент не найден")
        return None

class ProductScraper(WebScraper):
    def __init__(self, driver, product_url):
        super().__init__(driver)
        self.product_url = product_url

    def extract_product_details(self):
        self.driver.get(self.product_url)

        product_image_url = self.extract_product_image()
        if product_image_url:
            print("Фото товара:", product_image_url)

        product_name = self.extract_product_name()
        if product_name:
            print("Название товара:", product_name)

        product_price = self.extract_product_price()
        if product_price:
            print("Цена товара:", product_price)

        old_price = self.extract_old_price()
        if old_price:
            print("Зачеркнутая цена:", old_price)
        else:
            print("Зачеркнутая цена: отсутствует")

        product_rating, reviews_count = self.extract_rating_and_reviews_count()
        if product_rating and reviews_count:
            print(f"Общий рейтинг и количество отзывов: {product_rating} {reviews_count}")
        else:
            print("Отзывы и рейтинг отсутствуют")

    def extract_product_image(self):
        product_image_element = self.handle_exceptions(lambda: self.get_element(By.CSS_SELECTOR, "div.gallery_swiper img.gallery__thumb-img", timeout=20))
        if product_image_element:
            return product_image_element.get_attribute("src")
        return None

    def extract_product_name(self):
        product_name_element = self.handle_exceptions(lambda: self.get_element(By.CSS_SELECTOR, "h1.pdp-header__title"))
        if product_name_element:
            return product_name_element.text.strip()
        return None

    def extract_product_price(self):
        product_price_element = self.handle_exceptions(lambda: self.get_element(By.CSS_SELECTOR, "span.sales-block-offer-price__price-final"))
        if product_price_element:
            return product_price_element.text.strip()
        return None

    def extract_old_price(self):
        old_price_element = self.handle_exceptions(lambda: self.get_element(By.CSS_SELECTOR, "del.crossed-old-price-with-discount__crossed-old-price"))
        if old_price_element:
            return old_price_element.text.strip()
        return None

    def extract_rating_and_reviews_count(self):
        rating_wrapper_element = self.handle_exceptions(lambda: self.get_element(By.CSS_SELECTOR, "div.reviews-rating__counts-wrapper"))
        if rating_wrapper_element:
            try:
                rating_element = rating_wrapper_element.find_element(By.CSS_SELECTOR, "span.reviews-rating__reviews-rating-count")
                product_rating = rating_element.text.strip()
            except NoSuchElementException:
                product_rating = "Рейтинг отсутствует"

            try:
                reviews_count_element = rating_wrapper_element.find_element(By.CSS_SELECTOR, "span.reviews-rating__reviews-count")
                reviews_count = reviews_count_element.text.strip()
            except NoSuchElementException:
                reviews_count = "Отзывов нет"

            return product_rating, reviews_count
        return None, None

    def extract_reviews(self):
        while True:
            reviews_elements = self.handle_exceptions(lambda: self.get_elements(By.CSS_SELECTOR, "div.review-item"))
            if reviews_elements:
                for review_element in reviews_elements:
                    self.extract_review_details(review_element)
            else:
                print("Отзывы отсутствуют")
                break

            next_button = self.handle_exceptions(lambda: self.get_element(By.CSS_SELECTOR, "button.pagination-widget__page-link_next"))
            if next_button and "disabled" not in next_button.get_attribute("class"):
                next_button.click()
                time.sleep(2)  # Подождать, чтобы страница загрузилась
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.review-item")))
            else:
                break

    def extract_review_details(self, review_element):
        author_element = review_element.find_element(By.CSS_SELECTOR, "span.review-item-header__author")
        author = author_element.text.strip()

        pros = ""
        cons = ""
        comment = ""
        try:
            pros = review_element.find_element(By.XPATH, ".//p[text()='Достоинства']/following-sibling::div").text.strip()
        except NoSuchElementException:
            pros = "Не указаны"

        try:
            cons = review_element.find_element(By.XPATH, ".//p[text()='Недостатки']/following-sibling::div").text.strip()
        except NoSuchElementException:
            cons = "Не указаны"

        try:
            comment = review_element.find_element(By.XPATH, ".//p[text()='Комментарий']/following-sibling::div").text.strip()
        except NoSuchElementException:
            comment = "Отсутствует"

        print("Автор отзыва:", author)
        print("Достоинства:", pros)
        print("Недостатки:", cons)
        print("Комментарий:", comment)
        print("---")

def main():
    product_url = input("Введите ссылку на товар: ")

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    try:
        product_scraper = ProductScraper(driver, product_url)
        product_scraper.extract_product_details()
        product_scraper.extract_reviews()

    except Exception as e:
        print("Ошибка:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
