"""
Автоматизированные UI-тесты формы регистрации с использованием Selenium.
Запуск: python tests/test_form.py
"""

import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def get_driver():
    """Возвращает настроенный Chrome WebDriver (headless для CI)."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(options=options)
    return driver


def get_url():
    """Возвращает URL страницы (локальный файл или из переменной окружения)."""
    base = os.environ.get("TEST_URL", "")
    if base:
        return base.rstrip("/") + "/index.html"
    # Абсолютный путь к файлу для локального запуска
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return "file://" + here + "/index.html"


# ─── Тест 1: страница загружается и форма видна ──────────────────────────────

def test_page_loads():
    """Тест: страница загружается, заголовок и кнопка «Зарегистрироваться» присутствуют."""
    driver = get_driver()
    try:
        driver.get(get_url())
        wait = WebDriverWait(driver, 10)

        h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "Регистрация" in h1.text, f"Ожидался заголовок 'Регистрация', получено: {h1.text}"

        btn = driver.find_element(By.ID, "submit-btn")
        assert btn.is_displayed(), "Кнопка отправки не видна"
        assert "Зарегистрироваться" in btn.text
    finally:
        driver.quit()


# ─── Тест 2: успешная отправка заполненной формы ────────────────────────────

def test_successful_submission():
    """Тест: при корректном заполнении всех полей появляется сообщение об успехе."""
    driver = get_driver()
    try:
        driver.get(get_url())
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("Иван Иванов")
        driver.find_element(By.ID, "email").send_keys("ivan@example.com")
        driver.find_element(By.ID, "password").send_keys("secret123")

        select = Select(driver.find_element(By.ID, "role"))
        select.select_by_value("student")

        driver.find_element(By.ID, "submit-btn").click()

        msg = wait.until(EC.presence_of_element_located((By.ID, "message")))
        assert "успешно" in msg.text.lower(), f"Ожидалось слово 'успешно', получено: '{msg.text}'"
        assert "success" in msg.get_attribute("class"), "Сообщение не имеет класс success"
    finally:
        driver.quit()


# ─── Тест 3: ошибка при пустом email ────────────────────────────────────────

def test_empty_email_shows_error():
    """Тест: если email не введён, отображается ошибка."""
    driver = get_driver()
    try:
        driver.get(get_url())
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("Мария Петрова")
        # email оставляем пустым
        driver.find_element(By.ID, "password").send_keys("password1")

        select = Select(driver.find_element(By.ID, "role"))
        select.select_by_value("teacher")

        driver.find_element(By.ID, "submit-btn").click()

        msg = wait.until(EC.presence_of_element_located((By.ID, "message")))
        assert msg.text != "", "Сообщение об ошибке не появилось"
        assert "error" in msg.get_attribute("class"), "Класс ошибки отсутствует"
    finally:
        driver.quit()


# ─── Тест 4: ошибка при коротком пароле ─────────────────────────────────────

def test_short_password_shows_error():
    """Тест: пароль менее 6 символов вызывает ошибку."""
    driver = get_driver()
    try:
        driver.get(get_url())
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("Алексей")
        driver.find_element(By.ID, "email").send_keys("alex@example.com")
        driver.find_element(By.ID, "password").send_keys("123")  # слишком короткий

        select = Select(driver.find_element(By.ID, "role"))
        select.select_by_value("admin")

        driver.find_element(By.ID, "submit-btn").click()

        msg = wait.until(EC.presence_of_element_located((By.ID, "message")))
        assert "6" in msg.text or "минимум" in msg.text.lower(), \
            f"Ожидалось сообщение о длине пароля, получено: '{msg.text}'"
        assert "error" in msg.get_attribute("class")
    finally:
        driver.quit()


# ─── Точка входа (для запуска без pytest) ────────────────────────────────────

if __name__ == "__main__":
    import sys
    tests = [
        test_page_loads,
        test_successful_submission,
        test_empty_email_shows_error,
        test_short_password_shows_error,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except Exception as exc:
            print(f"  FAIL  {t.__name__}: {exc}")
            failed += 1
    sys.exit(failed)
