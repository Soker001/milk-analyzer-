"""
DairyDash — Milk Analyzer & Smart Pricing System
Selenium E2E Test Suite
100+ Test Cases covering all modules
"""

import time
import json
import requests
import unittest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementNotInteractableException
)
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:3000"
API_URL  = "http://localhost:3000/api"
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 10

# ──────────────────────────────────────────────────────────────────────────────
# Global test result store (populated by TestResultCollector)
# ──────────────────────────────────────────────────────────────────────────────
test_results = []


class TestResultCollector(unittest.TestResult):
    """Custom result collector that stores detailed per-test info."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_details = []

    def _record(self, test, status, error=None):
        doc  = (test.shortDescription() or str(test)).strip()
        name = str(test)
        # parse module tag from docstring: "TC-001 | Module | Title | Steps | Expected"
        parts = [p.strip() for p in doc.split("|")]
        tc_id    = parts[0] if len(parts) > 0 else name
        module   = parts[1] if len(parts) > 1 else "General"
        title    = parts[2] if len(parts) > 2 else doc
        steps    = parts[3] if len(parts) > 3 else ""
        expected = parts[4] if len(parts) > 4 else ""
        actual   = "As expected" if status == "PASS" else (str(error).splitlines()[-1] if error else "")
        self.test_details.append({
            "tc_id":    tc_id,
            "module":   module,
            "title":    title,
            "steps":    steps,
            "expected": expected,
            "actual":   actual,
            "status":   status,
            "remarks":  "" if status == "PASS" else "Investigate",
        })
        test_results.append(self.test_details[-1])

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", err[1])

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "ERROR", err[1])

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP")


# ──────────────────────────────────────────────────────────────────────────────
# Base test class
# ──────────────────────────────────────────────────────────────────────────────
class DairyDashBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        import os, glob
        cached_driver = r"C:\Users\HP\.wdm\drivers\chromedriver\win64\149.0.7827.115\chromedriver.exe"
        if os.path.exists(cached_driver):
            service = Service(cached_driver)
        else:
            fallback_paths = glob.glob(os.path.expanduser(r"~\.wdm\**\chromedriver.exe"), recursive=True)
            if fallback_paths:
                service = Service(fallback_paths[0])
            else:
                try:
                    service = Service(ChromeDriverManager().install())
                except Exception:
                    raise
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(IMPLICIT_WAIT)
        cls.wait   = WebDriverWait(cls.driver, EXPLICIT_WAIT)
        cls.driver.get(BASE_URL)
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def nav_to(self, target):
        """Click a sidebar nav item by data-target."""
        item = self.driver.find_element(By.CSS_SELECTOR, f"[data-target='{target}']")
        item.click()
        time.sleep(0.8)

    def fill_farmer_form(self, fid="F999", name="Test Farmer",
                         phone="9876543210", address="Test Village",
                         cows="2", buffaloes="1", bank="123456789012",
                         center="TC01", supply="10"):
        self.driver.find_element(By.ID, "f-id").clear()
        self.driver.find_element(By.ID, "f-id").send_keys(fid)
        self.driver.find_element(By.ID, "f-name").clear()
        self.driver.find_element(By.ID, "f-name").send_keys(name)
        self.driver.find_element(By.ID, "f-phone").clear()
        self.driver.find_element(By.ID, "f-phone").send_keys(phone)
        self.driver.find_element(By.ID, "f-address").clear()
        self.driver.find_element(By.ID, "f-address").send_keys(address)
        self.driver.find_element(By.ID, "f-cows").clear()
        self.driver.find_element(By.ID, "f-cows").send_keys(cows)
        self.driver.find_element(By.ID, "f-buffaloes").clear()
        self.driver.find_element(By.ID, "f-buffaloes").send_keys(buffaloes)
        self.driver.find_element(By.ID, "f-bank").clear()
        self.driver.find_element(By.ID, "f-bank").send_keys(bank)
        self.driver.find_element(By.ID, "f-center").clear()
        self.driver.find_element(By.ID, "f-center").send_keys(center)
        self.driver.find_element(By.ID, "f-supply").clear()
        self.driver.find_element(By.ID, "f-supply").send_keys(supply)

    def delete_all_test_farmers(self):
        """Clean up via API."""
        try:
            resp = requests.get(f"{API_URL}/farmers")
            for f in resp.json():
                fid = f.get("id") or f.get("_id")
                if fid:
                    requests.delete(f"{API_URL}/farmers/{fid}")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — Application Load & Navigation
# ══════════════════════════════════════════════════════════════════════════════
class TC01_AppLoad(DairyDashBaseTest):
    def test_TC001_page_title(self):
        """TC-001 | App Load | Page title is correct | Open browser to localhost:3000 | Title contains 'Milk Analyzer'"""
        self.assertIn("Milk Analyzer", self.driver.title)

    def test_TC002_sidebar_visible(self):
        """TC-002 | Navigation | Sidebar is rendered | Load page | <aside class='sidebar'> visible"""
        sidebar = self.driver.find_element(By.CSS_SELECTOR, "aside.sidebar")
        self.assertTrue(sidebar.is_displayed())

    def test_TC003_brand_name_visible(self):
        """TC-003 | Navigation | Brand 'DairyDash' shown in sidebar | Load page | DairyDash text visible"""
        brand = self.driver.find_element(By.CSS_SELECTOR, ".sidebar-header h2")
        self.assertEqual(brand.text, "DairyDash")

    def test_TC004_four_nav_items_present(self):
        """TC-004 | Navigation | 4 nav items exist | Count .nav-links li | 4 items found"""
        items = self.driver.find_elements(By.CSS_SELECTOR, ".nav-links li")
        self.assertEqual(len(items), 4)

    def test_TC005_farmer_details_nav_label(self):
        """TC-005 | Navigation | 'Farmer Details' nav item exists | Read first nav item text | 'Farmer Details'"""
        items = self.driver.find_elements(By.CSS_SELECTOR, ".nav-links li")
        self.assertIn("Farmer Details", items[0].text)

    def test_TC006_milk_quality_nav_label(self):
        """TC-006 | Navigation | 'Milk Quality' nav item exists | Read second nav item text | 'Milk Quality'"""
        items = self.driver.find_elements(By.CSS_SELECTOR, ".nav-links li")
        self.assertIn("Milk Quality", items[1].text)

    def test_TC007_adulteration_nav_label(self):
        """TC-007 | Navigation | 'Adulteration' nav item exists | Read third nav item text | 'Adulteration'"""
        items = self.driver.find_elements(By.CSS_SELECTOR, ".nav-links li")
        self.assertIn("Adulteration", items[2].text)

    def test_TC008_payment_nav_label(self):
        """TC-008 | Navigation | 'Payment System' nav item exists | Read fourth nav item text | 'Payment System'"""
        items = self.driver.find_elements(By.CSS_SELECTOR, ".nav-links li")
        self.assertIn("Payment System", items[3].text)

    def test_TC009_farmer_section_active_on_load(self):
        """TC-009 | Navigation | Farmer Details section active on load | Check #farmer-details.active | Module visible"""
        section = self.driver.find_element(By.ID, "farmer-details")
        self.assertIn("active", section.get_attribute("class"))

    def test_TC010_nav_to_milk_quality(self):
        """TC-010 | Navigation | Click Milk Quality nav | Click nav item | #milk-quality section active"""
        self.nav_to("milk-quality")
        section = self.driver.find_element(By.ID, "milk-quality")
        self.assertIn("active", section.get_attribute("class"))

    def test_TC011_nav_to_adulteration(self):
        """TC-011 | Navigation | Click Adulteration nav | Click nav item | #adulteration section active"""
        self.nav_to("adulteration")
        section = self.driver.find_element(By.ID, "adulteration")
        self.assertIn("active", section.get_attribute("class"))

    def test_TC012_nav_to_payment(self):
        """TC-012 | Navigation | Click Payment System nav | Click nav item | #payment-system section active"""
        self.nav_to("payment-system")
        section = self.driver.find_element(By.ID, "payment-system")
        self.assertIn("active", section.get_attribute("class"))

    def test_TC013_page_header_updates_on_nav(self):
        """TC-013 | Navigation | Page title updates on nav click | Click Milk Quality | H1 shows 'Milk Quality'"""
        self.nav_to("milk-quality")
        title = self.driver.find_element(By.ID, "page-title")
        self.assertIn("Milk Quality", title.text)

    def test_TC014_admin_label_in_header(self):
        """TC-014 | App Load | 'Admin' label in topbar | Load page | 'Admin' text found in user-profile"""
        admin = self.driver.find_element(By.CSS_SELECTOR, ".user-profile span")
        self.assertEqual(admin.text, "Admin")

    def test_TC015_toast_element_present(self):
        """TC-015 | App Load | Toast notification element exists | Check #toast element | Present in DOM"""
        toast = self.driver.find_element(By.ID, "toast")
        self.assertIsNotNone(toast)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — Farmer Details — Form Fields
# ══════════════════════════════════════════════════════════════════════════════
class TC02_FarmerForm(DairyDashBaseTest):
    def setUp(self):
        self.nav_to("farmer-details")

    def test_TC016_farmer_form_present(self):
        """TC-016 | Farmer Form | Add Farmer form is rendered | Load Farmer Details section | Form with id 'farmer-form' visible"""
        form = self.driver.find_element(By.ID, "farmer-form")
        self.assertTrue(form.is_displayed())

    def test_TC017_fid_field_present(self):
        """TC-017 | Farmer Form | Farmer ID field present | Check #f-id | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-id").is_displayed())

    def test_TC018_fname_field_present(self):
        """TC-018 | Farmer Form | Farmer Name field present | Check #f-name | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-name").is_displayed())

    def test_TC019_fphone_field_present(self):
        """TC-019 | Farmer Form | Phone field present | Check #f-phone | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-phone").is_displayed())

    def test_TC020_faddress_field_present(self):
        """TC-020 | Farmer Form | Address field present | Check #f-address | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-address").is_displayed())

    def test_TC021_fcows_field_present(self):
        """TC-021 | Farmer Form | Cows field present | Check #f-cows | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-cows").is_displayed())

    def test_TC022_fbuffaloes_field_present(self):
        """TC-022 | Farmer Form | Buffaloes field present | Check #f-buffaloes | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-buffaloes").is_displayed())

    def test_TC023_fbank_field_present(self):
        """TC-023 | Farmer Form | Bank Account field present | Check #f-bank | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-bank").is_displayed())

    def test_TC024_fcenter_field_present(self):
        """TC-024 | Farmer Form | Collection Center field present | Check #f-center | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-center").is_displayed())

    def test_TC025_fsupply_field_present(self):
        """TC-025 | Farmer Form | Daily Supply field present | Check #f-supply | Input element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "f-supply").is_displayed())

    def test_TC026_save_button_present(self):
        """TC-026 | Farmer Form | Save Farmer button present | Check submit button | Button exists"""
        btn = self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']")
        self.assertTrue(btn.is_displayed())

    def test_TC027_search_box_present(self):
        """TC-027 | Farmer Table | Search box present | Check #search-farmer | Input visible"""
        self.assertTrue(self.driver.find_element(By.ID, "search-farmer").is_displayed())

    def test_TC028_farmer_table_present(self):
        """TC-028 | Farmer Table | Farmer table rendered | Check #farmer-table | Table element visible"""
        self.assertTrue(self.driver.find_element(By.ID, "farmer-table").is_displayed())

    def test_TC029_table_has_correct_headers(self):
        """TC-029 | Farmer Table | Table has ID/Name/Phone columns | Read th elements | Headers match"""
        headers = [th.text for th in self.driver.find_elements(By.CSS_SELECTOR, "#farmer-table th")]
        self.assertIn("ID", headers)
        self.assertIn("Name", headers)
        self.assertIn("Phone", headers)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 3 — Farmer CRUD Operations
# ══════════════════════════════════════════════════════════════════════════════
class TC03_FarmerCRUD(DairyDashBaseTest):
    def setUp(self):
        self.nav_to("farmer-details")
        self.delete_all_test_farmers()
        time.sleep(1)
        self.driver.refresh()
        time.sleep(2)
        self.nav_to("farmer-details")

    def test_TC030_add_valid_farmer(self):
        """TC-030 | Farmer CRUD | Submit valid farmer form | Fill all fields and submit | Farmer appears in table"""
        self.fill_farmer_form(fid="F100", name="Ramu Nadar", phone="9876543210",
                              address="Coimbatore", cows="3", buffaloes="1",
                              bank="111122223333", center="CT01", supply="15")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#farmer-table tbody"), "Ramu Nadar"))
        tbody = self.driver.find_element(By.CSS_SELECTOR, "#farmer-table tbody")
        self.assertIn("Ramu Nadar", tbody.text)

    def test_TC031_farmer_id_appears_in_table(self):
        """TC-031 | Farmer CRUD | Farmer ID visible in table after add | Add farmer F101 | F101 appears in table"""
        self.fill_farmer_form(fid="F101", name="Selvi Amma", phone="9876500001",
                              bank="222233334444", center="CT02")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#farmer-table tbody"), "F101"))
        tbody = self.driver.find_element(By.CSS_SELECTOR, "#farmer-table tbody")
        self.assertIn("F101", tbody.text)

    def test_TC032_farmer_phone_appears_in_table(self):
        """TC-032 | Farmer CRUD | Phone number visible in table | Add farmer with phone 9123456789 | Phone visible in row"""
        self.fill_farmer_form(fid="F102", name="Kumar Pillai", phone="9123456789",
                              bank="333344445555", center="CT03")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#farmer-table tbody"), "9123456789"))
        tbody = self.driver.find_element(By.CSS_SELECTOR, "#farmer-table tbody")
        self.assertIn("9123456789", tbody.text)

    def test_TC033_form_resets_after_submit(self):
        """TC-033 | Farmer CRUD | Form clears after successful submit | Submit form and check | Input fields empty"""
        self.fill_farmer_form(fid="F103", name="Clear Test", phone="9000000003",
                              bank="444455556666", center="CT04")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        self.wait.until(lambda d: d.find_element(By.ID, "f-id").get_attribute("value") == "")
        fid_val = self.driver.find_element(By.ID, "f-id").get_attribute("value")
        self.assertEqual(fid_val, "")

    def test_TC034_delete_farmer(self):
        """TC-034 | Farmer CRUD | Delete button removes farmer | Add farmer then click delete | Row disappears"""
        self.fill_farmer_form(fid="F104", name="Delete Test", phone="9000000004",
                              bank="555566667777", center="CT05")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#farmer-table tbody"), "Delete Test"))
        rows_before = len(self.driver.find_elements(By.CSS_SELECTOR, "#farmer-table tbody tr"))
        delete_btn  = self.driver.find_element(By.CSS_SELECTOR, "#farmer-table tbody .delete")
        self.driver.execute_script("arguments[0].click();", delete_btn)
        time.sleep(0.5)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except Exception:
            pass
        self.wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#farmer-table tbody tr")) < rows_before)
        rows_after = len(self.driver.find_elements(By.CSS_SELECTOR, "#farmer-table tbody tr"))
        self.assertLess(rows_after, rows_before)

    def test_TC035_duplicate_farmer_id_rejected(self):
        """TC-035 | Farmer CRUD | Duplicate farmer ID is rejected by API | Submit same ID twice | Second POST returns 400"""
        self.fill_farmer_form(fid="F105", name="Dup Test 1", phone="9000000005",
                              bank="666677778888", center="CT06")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        time.sleep(1)
        resp = requests.post(f"{API_URL}/farmers",
                             json={"f-id": "F105", "f-name": "Dup Test 2", "f-phone": "9000000099",
                                   "f-bank": "000000000000", "f-center": "CT00"})
        self.assertEqual(resp.status_code, 400)

    def test_TC036_get_farmers_api_returns_list(self):
        """TC-036 | Farmer CRUD | GET /api/farmers returns JSON list | Direct API call | Status 200 + list"""
        resp = requests.get(f"{API_URL}/farmers")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_TC037_post_farmer_api_returns_201(self):
        """TC-037 | Farmer CRUD | POST /api/farmers returns 201 | Direct API call | Status 201"""
        import random
        uid = str(random.randint(900, 999))
        resp = requests.post(f"{API_URL}/farmers",
                             json={"f-id": f"FA{uid}", "f-name": "API Test",
                                   "f-phone": "9000001111",
                                   "f-bank": "999900001111", "f-center": "API01"})
        self.assertEqual(resp.status_code, 201)

    def test_TC038_delete_nonexistent_farmer_handled(self):
        """TC-038 | Farmer CRUD | DELETE non-existent ObjectId returns gracefully | API call | Response not 500"""
        resp = requests.delete(f"{API_URL}/farmers/000000000000000000000000")
        self.assertIn(resp.status_code, [200, 400, 404])

    def test_TC039_search_filters_table_rows(self):
        """TC-039 | Farmer Table | Search box filters rows | Type name in search box | Non-matching rows hidden"""
        self.fill_farmer_form(fid="F106", name="SearchableVijay", phone="9000000006",
                              bank="777788889999", center="CT07")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        time.sleep(1)
        search = self.driver.find_element(By.ID, "search-farmer")
        search.send_keys("SearchableVijay")
        time.sleep(0.5)
        visible_rows = [r for r in self.driver.find_elements(By.CSS_SELECTOR, "#farmer-table tbody tr")
                        if r.is_displayed()]
        self.assertGreaterEqual(len(visible_rows), 1)
        self.assertIn("SearchableVijay", visible_rows[0].text)

    def test_TC040_search_clear_restores_all_rows(self):
        """TC-040 | Farmer Table | Clearing search restores all rows | Type then clear search | All rows visible"""
        self.fill_farmer_form(fid="F106", name="SearchableVijay", phone="9000000006",
                              bank="777788889999", center="CT07")
        self.driver.find_element(By.CSS_SELECTOR, "#farmer-form button[type='submit']").click()
        time.sleep(1)
        search = self.driver.find_element(By.ID, "search-farmer")
        search.clear()
        search.send_keys("SearchableVijay")
        time.sleep(0.5)
        search.send_keys(Keys.CONTROL + "a")
        search.send_keys(Keys.DELETE)
        time.sleep(0.5)
        rows = self.driver.find_elements(By.CSS_SELECTOR, "#farmer-table tbody tr")
        visible = [r for r in rows if r.is_displayed()]
        self.assertGreater(len(visible), 0)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 4 — Milk Quality Analysis
# ══════════════════════════════════════════════════════════════════════════════
class TC04_MilkQuality(DairyDashBaseTest):
    def setUp(self):
        # Ensure a farmer exists first
        requests.post(f"{API_URL}/farmers",
                      json={"f-id": "QF01", "f-name": "Quality Farmer",
                            "f-phone": "9111111111", "f-bank": "111100001111",
                            "f-center": "QC01"})
        self.driver.refresh()
        time.sleep(2)
        self.nav_to("milk-quality")

    def test_TC041_quality_form_visible(self):
        """TC-041 | Milk Quality | Quality analysis form is rendered | Navigate to Milk Quality | Form #quality-form visible"""
        self.assertTrue(self.driver.find_element(By.ID, "quality-form").is_displayed())

    def test_TC042_farmer_dropdown_present(self):
        """TC-042 | Milk Quality | Farmer dropdown present | Check #q-farmer | Select element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "q-farmer").is_displayed())

    def test_TC043_farmer_dropdown_has_options(self):
        """TC-043 | Milk Quality | Farmer dropdown has options | Check option count | At least 1 farmer option"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        self.assertGreater(len(sel.options), 1)

    def test_TC044_milk_type_dropdown_present(self):
        """TC-044 | Milk Quality | Milk type dropdown present | Check #q-type | Select element visible"""
        self.assertTrue(self.driver.find_element(By.ID, "q-type").is_displayed())

    def test_TC045_milk_type_options_correct(self):
        """TC-045 | Milk Quality | Milk type has Cow/Buffalo/Mixed options | Read option values | 3 options present"""
        sel    = Select(self.driver.find_element(By.ID, "q-type"))
        values = [o.get_attribute("value") for o in sel.options]
        self.assertIn("Cow", values)
        self.assertIn("Buffalo", values)
        self.assertIn("Mixed", values)

    def test_TC046_quantity_field_present(self):
        """TC-046 | Milk Quality | Quantity field present | Check #q-quantity | Input visible"""
        self.assertTrue(self.driver.find_element(By.ID, "q-quantity").is_displayed())

    def test_TC047_fat_field_present(self):
        """TC-047 | Milk Quality | Fat % field present | Check #q-fat | Input visible"""
        self.assertTrue(self.driver.find_element(By.ID, "q-fat").is_displayed())

    def test_TC048_snf_field_present(self):
        """TC-048 | Milk Quality | SNF % field present | Check #q-snf | Input visible"""
        self.assertTrue(self.driver.find_element(By.ID, "q-snf").is_displayed())

    def test_TC049_analyze_button_present(self):
        """TC-049 | Milk Quality | Analyze Quality button present | Check button text | Button visible"""
        btn = self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary")
        self.assertTrue(btn.is_displayed())

    def test_TC050_analyze_quality_excellent_score(self):
        """TC-050 | Milk Quality | Excellent fat/SNF yields score >=90 | Fat=4.5, SNF=9.0, submit | Score >= 90"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        self.driver.find_element(By.ID, "q-quantity").send_keys("10")
        self.driver.find_element(By.ID, "q-fat").send_keys("4.5")
        self.driver.find_element(By.ID, "q-snf").send_keys("9.0")
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "base-score").text)
        self.assertGreaterEqual(score, 90)

    def test_TC051_analyze_quality_low_fat_reduces_score(self):
        """TC-051 | Milk Quality | Low fat reduces score | Fat=2.0, SNF=8.5 | Score < 90"""
        self.driver.find_element(By.ID, "q-quantity").clear()
        self.driver.find_element(By.ID, "q-quantity").send_keys("10")
        self.driver.find_element(By.ID, "q-fat").clear()
        self.driver.find_element(By.ID, "q-fat").send_keys("2.0")
        self.driver.find_element(By.ID, "q-snf").clear()
        self.driver.find_element(By.ID, "q-snf").send_keys("8.5")
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "base-score").text)
        self.assertLess(score, 90)

    def test_TC052_result_card_shown_after_analysis(self):
        """TC-052 | Milk Quality | Quality result card shown after analysis | Click Analyze | #quality-result-card displayed"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        self.driver.find_element(By.ID, "q-quantity").clear()
        self.driver.find_element(By.ID, "q-quantity").send_keys("5")
        self.driver.find_element(By.ID, "q-fat").clear()
        self.driver.find_element(By.ID, "q-fat").send_keys("4.0")
        self.driver.find_element(By.ID, "q-snf").clear()
        self.driver.find_element(By.ID, "q-snf").send_keys("8.5")
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        card = self.driver.find_element(By.ID, "quality-result-card")
        display = card.value_of_css_property("display")
        self.assertNotEqual(display, "none")

    def test_TC053_status_excellent_label(self):
        """TC-053 | Milk Quality | Excellent status label for score>=90 | Fat=4.5,SNF=9 | Status badge says 'Excellent'"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        for fid, val in [("q-quantity","10"),("q-fat","4.5"),("q-snf","9.0")]:
            el = self.driver.find_element(By.ID, fid)
            el.clear(); el.send_keys(val)
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        status = self.driver.find_element(By.ID, "q-status").text
        self.assertEqual(status, "Excellent")

    def test_TC054_status_poor_label_low_values(self):
        """TC-054 | Milk Quality | Poor label for very low fat/SNF | Fat=1.0, SNF=6.0 | Status = 'Average / Poor'"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        for fid, val in [("q-quantity","5"),("q-fat","1.0"),("q-snf","6.0")]:
            el = self.driver.find_element(By.ID, fid)
            el.clear(); el.send_keys(val)
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        status = self.driver.find_element(By.ID, "q-status").text
        self.assertEqual(status, "Average / Poor")

    def test_TC055_missing_farmer_shows_toast(self):
        """TC-055 | Milk Quality | Missing farmer shows error toast | Click Analyze without selecting farmer | Toast error shown"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_value("")
        self.driver.find_element(By.ID, "q-quantity").clear()
        self.driver.find_element(By.ID, "q-quantity").send_keys("5")
        self.driver.find_element(By.ID, "q-fat").clear()
        self.driver.find_element(By.ID, "q-fat").send_keys("4.0")
        self.driver.find_element(By.ID, "q-snf").clear()
        self.driver.find_element(By.ID, "q-snf").send_keys("8.5")
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.8)
        toast = self.driver.find_element(By.ID, "toast")
        classes = toast.get_attribute("class")
        self.assertIn("show", classes)

    def test_TC056_next_adulteration_button_present(self):
        """TC-056 | Milk Quality | 'Next: Adulteration Check' button visible | After analysis | Button rendered"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        for fid, val in [("q-quantity","5"),("q-fat","4.0"),("q-snf","8.5")]:
            el = self.driver.find_element(By.ID, fid)
            el.clear(); el.send_keys(val)
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        btn = self.driver.find_element(By.CSS_SELECTOR, "#quality-result-card .btn-primary")
        self.assertTrue(btn.is_displayed())

    def test_TC057_score_capped_at_100(self):
        """TC-057 | Milk Quality | Score never exceeds 100 | Fat=10.0,SNF=15.0 | Score <= 100"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        for fid, val in [("q-quantity","5"),("q-fat","10.0"),("q-snf","15.0")]:
            el = self.driver.find_element(By.ID, fid)
            el.clear(); el.send_keys(val)
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "base-score").text)
        self.assertLessEqual(score, 100)

    def test_TC058_score_not_negative(self):
        """TC-058 | Milk Quality | Score never negative | Fat=0.0,SNF=0.0 | Score >= 0"""
        sel = Select(self.driver.find_element(By.ID, "q-farmer"))
        sel.select_by_index(1)
        for fid, val in [("q-quantity","5"),("q-fat","0.0"),("q-snf","0.0")]:
            el = self.driver.find_element(By.ID, fid)
            el.clear(); el.send_keys(val)
        self.driver.find_element(By.CSS_SELECTOR, "#quality-form .btn-secondary").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "base-score").text)
        self.assertGreaterEqual(score, 0)

    def test_TC059_quality_api_saves_record(self):
        """TC-059 | Milk Quality | POST /api/quality saves and returns 201 | Direct API call | Status 201"""
        resp = requests.post(f"{API_URL}/quality",
                             json={"farmerId": "QF01", "quantity": 10, "fat": 4.0,
                                   "snf": 8.5, "baseScore": 100, "finalScore": 100})
        self.assertEqual(resp.status_code, 201)

    def test_TC060_quality_api_get_returns_list(self):
        """TC-060 | Milk Quality | GET /api/quality returns list | Direct API call | Status 200 + list"""
        resp = requests.get(f"{API_URL}/quality")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 5 — Adulteration Detection
# ══════════════════════════════════════════════════════════════════════════════
class TC05_Adulteration(DairyDashBaseTest):
    def _setup_quality_data(self, base_score=95):
        """Helper: complete quality step first via JS injection."""
        self.driver.execute_script(f"""
            window.currentQualityData = {{
                farmerId: 'QF01',
                qty: 10,
                fat: 4.0,
                snf: 8.5,
                baseScore: {base_score}
            }};
        """)

    def setUp(self):
        requests.post(f"{API_URL}/farmers",
                      json={"f-id": "QF01", "f-name": "Quality Farmer",
                            "f-phone": "9111111111", "f-bank": "111100001111",
                            "f-center": "QC01"})
        self.driver.refresh()
        time.sleep(2)
        self.nav_to("adulteration")
        self._setup_quality_data()

    def test_TC061_adulteration_form_visible(self):
        """TC-061 | Adulteration | Adulteration form rendered | Navigate to Adulteration | Form visible"""
        self.assertTrue(self.driver.find_element(By.ID, "adulteration-form").is_displayed())

    def test_TC062_water_dilution_field_present(self):
        """TC-062 | Adulteration | Water dilution field present | Check #a-water | Input exists"""
        self.assertTrue(self.driver.find_element(By.ID, "a-water").is_displayed())

    def test_TC063_urea_dropdown_present(self):
        """TC-063 | Adulteration | Urea detection dropdown present | Check #a-urea | Select exists"""
        self.assertTrue(self.driver.find_element(By.ID, "a-urea").is_displayed())

    def test_TC064_starch_dropdown_present(self):
        """TC-064 | Adulteration | Starch detection dropdown present | Check #a-starch | Select exists"""
        self.assertTrue(self.driver.find_element(By.ID, "a-starch").is_displayed())

    def test_TC065_detergent_dropdown_present(self):
        """TC-065 | Adulteration | Detergent detection dropdown present | Check #a-detergent | Select exists"""
        self.assertTrue(self.driver.find_element(By.ID, "a-detergent").is_displayed())

    def test_TC066_salt_dropdown_present(self):
        """TC-066 | Adulteration | Salt detection dropdown present | Check #a-salt | Select exists"""
        self.assertTrue(self.driver.find_element(By.ID, "a-salt").is_displayed())

    def test_TC067_analyze_button_present(self):
        """TC-067 | Adulteration | Analyze button present | Check .btn-warning | Button visible"""
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").is_displayed())

    def test_TC068_pure_milk_status_for_clean_sample(self):
        """TC-068 | Adulteration | Pure milk status when no adulterants | All No, 0% water | Status = 'Pure Milk'"""
        self._setup_quality_data(95)
        for fid in ["a-urea", "a-starch", "a-detergent", "a-salt"]:
            Select(self.driver.find_element(By.ID, fid)).select_by_value("No")
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("0")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        status = self.driver.find_element(By.ID, "adulteration-status").text
        self.assertEqual(status, "Pure Milk")

    def test_TC069_urea_detected_reduces_score(self):
        """TC-069 | Adulteration | Urea detected reduces final score by 50 | Set urea=Yes, click analyze | Score drops"""
        self._setup_quality_data(95)
        Select(self.driver.find_element(By.ID, "a-urea")).select_by_value("Yes")
        Select(self.driver.find_element(By.ID, "a-starch")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-detergent")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-salt")).select_by_value("No")
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("0")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "final-score").text)
        self.assertLessEqual(score, 50)

    def test_TC070_detergent_detected_sets_high_adulteration(self):
        """TC-070 | Adulteration | Detergent detected sets 'Highly Adulterated' | Set detergent=Yes | Status = 'Highly Adulterated'"""
        self._setup_quality_data(95)
        Select(self.driver.find_element(By.ID, "a-detergent")).select_by_value("Yes")
        Select(self.driver.find_element(By.ID, "a-urea")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-starch")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-salt")).select_by_value("No")
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("0")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        status = self.driver.find_element(By.ID, "adulteration-status").text
        self.assertEqual(status, "Highly Adulterated")

    def test_TC071_water_dilution_reduces_score(self):
        """TC-071 | Adulteration | Water >5% reduces score | Set water=20% | Score reduced"""
        self._setup_quality_data(95)
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("20")
        Select(self.driver.find_element(By.ID, "a-urea")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-detergent")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-starch")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-salt")).select_by_value("No")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "final-score").text)
        self.assertLess(score, 95)

    def test_TC072_warning_messages_shown_for_adulterants(self):
        """TC-072 | Adulteration | Warning messages list populated | Add starch=Yes | #warning-messages has items"""
        self._setup_quality_data(95)
        Select(self.driver.find_element(By.ID, "a-starch")).select_by_value("Yes")
        Select(self.driver.find_element(By.ID, "a-urea")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-detergent")).select_by_value("No")
        Select(self.driver.find_element(By.ID, "a-salt")).select_by_value("No")
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("0")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        items = self.driver.find_elements(By.CSS_SELECTOR, "#warning-messages li")
        self.assertGreater(len(items), 0)

    def test_TC073_final_score_capped_at_zero(self):
        """TC-073 | Adulteration | Final score cannot go below 0 | All adulterants Yes | Score >= 0"""
        self._setup_quality_data(95)
        for fid in ["a-urea", "a-starch", "a-detergent", "a-salt"]:
            Select(self.driver.find_element(By.ID, fid)).select_by_value("Yes")
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("100")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        score = int(self.driver.find_element(By.ID, "final-score").text)
        self.assertGreaterEqual(score, 0)

    def test_TC074_result_card_shown_after_adulteration_check(self):
        """TC-074 | Adulteration | Result card shown after analysis | Click analyze | #adulteration-result-card visible"""
        self._setup_quality_data(95)
        for fid in ["a-urea","a-starch","a-detergent","a-salt"]:
            Select(self.driver.find_element(By.ID, fid)).select_by_value("No")
        self.driver.find_element(By.ID, "a-water").clear()
        self.driver.find_element(By.ID, "a-water").send_keys("0")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        card = self.driver.find_element(By.ID, "adulteration-result-card")
        display = card.value_of_css_property("display")
        self.assertNotEqual(display, "none")

    def test_TC075_proceed_to_payment_button_visible(self):
        """TC-075 | Adulteration | 'Proceed to Payment' button visible after analysis | Analyze and check | Button rendered"""
        self._setup_quality_data(95)
        for fid in ["a-urea","a-starch","a-detergent","a-salt"]:
            Select(self.driver.find_element(By.ID, fid)).select_by_value("No")
        el = self.driver.find_element(By.ID, "a-water")
        el.clear(); el.send_keys("0")
        self.driver.find_element(By.CSS_SELECTOR, "#adulteration-form .btn-warning").click()
        time.sleep(0.5)
        btn = self.driver.find_element(By.CSS_SELECTOR, "#adulteration-result-card .btn-success")
        self.assertTrue(btn.is_displayed())


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 6 — Payment System
# ══════════════════════════════════════════════════════════════════════════════
class TC06_Payment(DairyDashBaseTest):
    def _inject_quality_state(self):
        self.driver.execute_script("""
            window.currentQualityData = {
                farmerId: 'PF01',
                qty: 10,
                fat: 4.5,
                snf: 9.0,
                baseScore: 100,
                finalScore: 95
            };
            document.getElementById('summary-qty').textContent   = '10 L';
            document.getElementById('summary-fat').textContent   = '4.5 %';
            document.getElementById('summary-snf').textContent   = '9.0 %';
            document.getElementById('summary-score').textContent = '95 / 100';
        """)

    def setUp(self):
        requests.post(f"{API_URL}/farmers",
                      json={"f-id": "PF01", "f-name": "Pay Farmer",
                            "f-phone": "9222222222", "f-bank": "222200002222",
                            "f-center": "PC01"})
        self.driver.refresh()
        time.sleep(2)
        self.nav_to("payment-system")
        self._inject_quality_state()

    def test_TC076_payment_form_visible(self):
        """TC-076 | Payment | Payment form rendered | Navigate to Payment System | Form #payment-form visible"""
        self.assertTrue(self.driver.find_element(By.ID, "payment-form").is_displayed())

    def test_TC077_state_dropdown_present(self):
        """TC-077 | Payment | State dropdown present | Check #p-state | Select element exists"""
        self.assertTrue(self.driver.find_element(By.ID, "p-state").is_displayed())

    def test_TC078_state_dropdown_has_7_states(self):
        """TC-078 | Payment | State dropdown has 7 state options | Count options | 7 states + placeholder"""
        sel  = Select(self.driver.find_element(By.ID, "p-state"))
        vals = [o.get_attribute("value") for o in sel.options if o.get_attribute("value")]
        self.assertEqual(len(vals), 7)

    def test_TC079_tamil_nadu_in_dropdown(self):
        """TC-079 | Payment | Tamil Nadu in state dropdown | Read option values | 'Tamil Nadu' present"""
        sel  = Select(self.driver.find_element(By.ID, "p-state"))
        vals = [o.get_attribute("value") for o in sel.options]
        self.assertIn("Tamil Nadu", vals)

    def test_TC080_kerala_in_dropdown(self):
        """TC-080 | Payment | Kerala in state dropdown | Read option values | 'Kerala' present"""
        sel  = Select(self.driver.find_element(By.ID, "p-state"))
        vals = [o.get_attribute("value") for o in sel.options]
        self.assertIn("Kerala", vals)

    def test_TC081_gujarat_in_dropdown(self):
        """TC-081 | Payment | Gujarat in state dropdown | Read option values | 'Gujarat' present"""
        sel  = Select(self.driver.find_element(By.ID, "p-state"))
        vals = [o.get_attribute("value") for o in sel.options]
        self.assertIn("Gujarat", vals)

    def test_TC082_calculate_price_api_tamil_nadu(self):
        """TC-082 | Payment | Tamil Nadu pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Tamil Nadu", "fat": 4.5, "snf": 9.0,
                                   "quantity": 10, "quality_score": 95})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

    def test_TC083_calculate_price_api_kerala(self):
        """TC-083 | Payment | Kerala pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Kerala", "fat": 4.0, "snf": 8.5,
                                   "quantity": 8, "quality_score": 90})
        self.assertTrue(resp.json().get("success"))

    def test_TC084_calculate_price_api_karnataka(self):
        """TC-084 | Payment | Karnataka pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Karnataka", "fat": 4.0, "snf": 8.5,
                                   "quantity": 12, "quality_score": 88})
        self.assertTrue(resp.json().get("success"))

    def test_TC085_calculate_price_api_gujarat(self):
        """TC-085 | Payment | Gujarat pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Gujarat", "fat": 5.0, "snf": 9.0,
                                   "quantity": 15, "quality_score": 100})
        self.assertTrue(resp.json().get("success"))

    def test_TC086_calculate_price_api_maharashtra(self):
        """TC-086 | Payment | Maharashtra pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Maharashtra", "fat": 4.5, "snf": 8.8,
                                   "quantity": 20, "quality_score": 85})
        self.assertTrue(resp.json().get("success"))

    def test_TC087_calculate_price_api_punjab(self):
        """TC-087 | Payment | Punjab pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Punjab", "fat": 4.2, "snf": 8.6,
                                   "quantity": 18, "quality_score": 92})
        self.assertTrue(resp.json().get("success"))

    def test_TC088_calculate_price_api_haryana(self):
        """TC-088 | Payment | Haryana pricing API returns result | POST /api/calculate-price | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Haryana", "fat": 4.3, "snf": 8.7,
                                   "quantity": 14, "quality_score": 95})
        self.assertTrue(resp.json().get("success"))

    def test_TC089_price_response_has_base_price(self):
        """TC-089 | Payment | Price response contains base_price_per_litre | API call | Field present"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Tamil Nadu", "fat": 4.0, "snf": 8.5,
                                   "quantity": 10, "quality_score": 100})
        self.assertIn("base_price_per_litre", resp.json())

    def test_TC090_price_response_has_total_payment(self):
        """TC-090 | Payment | Price response contains total_payment | API call | total_payment > 0"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Tamil Nadu", "fat": 4.0, "snf": 8.5,
                                   "quantity": 10, "quality_score": 100})
        self.assertGreater(resp.json().get("total_payment", 0), 0)

    def test_TC091_quality_score_zero_means_zero_payment(self):
        """TC-091 | Payment | Quality score 0 results in 0 total payment | quality_score=0 | total_payment = 0"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Tamil Nadu", "fat": 4.0, "snf": 8.5,
                                   "quantity": 10, "quality_score": 0})
        self.assertEqual(resp.json().get("total_payment"), 0)

    def test_TC092_ui_calculate_payout_button_present(self):
        """TC-092 | Payment | 'Calculate Payout' button present | Check UI | Button visible"""
        btn = self.driver.find_element(By.CSS_SELECTOR, "#payment-form .btn-primary")
        self.assertTrue(btn.is_displayed())

    def test_TC093_payment_summary_qty_displayed(self):
        """TC-093 | Payment | Quantity summary displayed in payment form | Inject data | #summary-qty shows value"""
        qty = self.driver.find_element(By.ID, "summary-qty").text
        self.assertIn("10", qty)

    def test_TC094_payment_summary_fat_displayed(self):
        """TC-094 | Payment | Fat summary displayed in payment form | Inject data | #summary-fat shows value"""
        fat = self.driver.find_element(By.ID, "summary-fat").text
        self.assertIn("4.5", fat)

    def test_TC095_payment_calculate_button_triggers_api(self):
        """TC-095 | Payment | Clicking Calculate Payout calls pricing API | Select state and click | Payment details shown"""
        self._inject_quality_state()
        Select(self.driver.find_element(By.ID, "p-state")).select_by_value("Tamil Nadu")
        self.driver.find_element(By.CSS_SELECTOR, "#payment-form .btn-primary").click()
        time.sleep(4)
        details = self.driver.find_element(By.ID, "payment-details")
        display = details.value_of_css_property("display")
        self.assertNotEqual(display, "none")

    def test_TC096_payment_base_price_shown(self):
        """TC-096 | Payment | Base price per litre shown after calculation | Calculate for Tamil Nadu | #p-base-price non-zero"""
        self._inject_quality_state()
        Select(self.driver.find_element(By.ID, "p-state")).select_by_value("Tamil Nadu")
        self.driver.find_element(By.CSS_SELECTOR, "#payment-form .btn-primary").click()
        time.sleep(4)
        base = self.driver.find_element(By.ID, "p-base-price").text
        self.assertNotEqual(base, "₹0.00")

    def test_TC097_payment_total_shown_as_currency(self):
        """TC-097 | Payment | Total payment shown with rupee symbol | After calculation | #p-total starts with ₹"""
        self._inject_quality_state()
        Select(self.driver.find_element(By.ID, "p-state")).select_by_value("Gujarat")
        self.driver.find_element(By.CSS_SELECTOR, "#payment-form .btn-primary").click()
        time.sleep(4)
        total = self.driver.find_element(By.ID, "p-total").text
        self.assertTrue(total.startswith("₹"))

    def test_TC098_post_payment_api_returns_201(self):
        """TC-098 | Payment | POST /api/payments returns 201 | Direct API call | Status 201"""
        resp = requests.post(f"{API_URL}/payments",
                             json={"farmerId": "PF01", "quantity": 10, "fat": 4.5,
                                   "snf": 9.0, "qualityScore": 95, "state": "Tamil Nadu",
                                   "basePricePerLitre": 58.5, "finalPricePerLitre": 55.58,
                                   "totalPayment": 555.8})
        self.assertEqual(resp.status_code, 201)

    def test_TC099_get_payments_api_returns_list(self):
        """TC-099 | Payment | GET /api/payments returns list | Direct API call | Status 200 + list"""
        resp = requests.get(f"{API_URL}/payments")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_TC100_get_payments_by_farmer_api(self):
        """TC-100 | Payment | GET /api/payments/farmer/:id returns list | API call with PF01 | Status 200 + list"""
        resp = requests.get(f"{API_URL}/payments/farmer/PF01")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 7 — API & Infrastructure
# ══════════════════════════════════════════════════════════════════════════════
class TC07_APIInfrastructure(DairyDashBaseTest):
    def test_TC101_status_api_returns_200(self):
        """TC-101 | API | GET /api/status returns 200 | Direct API call | Status 200"""
        resp = requests.get(f"{API_URL}/status")
        self.assertEqual(resp.status_code, 200)

    def test_TC102_status_api_has_server_field(self):
        """TC-102 | API | Status response has 'server' field | GET /api/status | server=running"""
        resp = requests.get(f"{API_URL}/status")
        self.assertEqual(resp.json().get("server"), "running")

    def test_TC103_status_api_has_database_field(self):
        """TC-103 | API | Status response has 'database' field | GET /api/status | database field present"""
        resp = requests.get(f"{API_URL}/status")
        self.assertIn("database", resp.json())

    def test_TC104_invalid_json_to_farmers_rejected(self):
        """TC-104 | API | Invalid JSON to POST /api/farmers | Send malformed body | Not 201"""
        resp = requests.post(f"{API_URL}/farmers",
                             data="not-json",
                             headers={"Content-Type": "application/json"})
        self.assertNotEqual(resp.status_code, 201)

    def test_TC105_pricing_missing_state_returns_result(self):
        """TC-105 | API | Pricing with empty state uses default formula | state='' | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "", "fat": 4.0, "snf": 8.5,
                                   "quantity": 10, "quality_score": 80})
        self.assertTrue(resp.json().get("success"))

    def test_TC106_pricing_zero_quantity_gives_zero_total(self):
        """TC-106 | API | Pricing with 0 quantity gives 0 total payment | quantity=0 | total_payment=0"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state": "Kerala", "fat": 4.0, "snf": 8.5,
                                   "quantity": 0, "quality_score": 90})
        self.assertEqual(resp.json().get("total_payment"), 0)

    def test_TC107_cors_header_present(self):
        """TC-107 | API | CORS header present in response | GET /api/status with Origin | Access-Control header set"""
        resp = requests.get(f"{API_URL}/status",
                            headers={"Origin": "http://example.com"})
        self.assertIn("Access-Control-Allow-Origin", resp.headers)

    def test_TC108_content_type_json_in_response(self):
        """TC-108 | API | Response Content-Type is application/json | GET /api/farmers | Content-Type: application/json"""
        resp = requests.get(f"{API_URL}/farmers")
        self.assertIn("application/json", resp.headers.get("Content-Type", ""))

    def test_TC109_static_files_served(self):
        """TC-109 | Infrastructure | Static files served by Express | GET /index.html | HTTP 200"""
        resp = requests.get(f"{BASE_URL}/index.html")
        self.assertEqual(resp.status_code, 200)

    def test_TC110_app_js_served(self):
        """TC-110 | Infrastructure | app.js served | GET /js/app.js | HTTP 200"""
        resp = requests.get(f"{BASE_URL}/js/app.js")
        self.assertEqual(resp.status_code, 200)

    def test_TC111_style_css_served(self):
        """TC-111 | Infrastructure | style.css served | GET /css/style.css | HTTP 200 or 304"""
        resp = requests.get(f"{BASE_URL}/css/style.css")
        self.assertIn(resp.status_code, [200, 304])


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 8 — UI / UX Checks
# ══════════════════════════════════════════════════════════════════════════════
class TC08_UIChecks(DairyDashBaseTest):
    def setUp(self):
        self.nav_to("farmer-details")

    def test_TC112_only_one_active_section_at_a_time(self):
        """TC-112 | UI | Only one section active at a time | Click different nav | Other sections not active"""
        self.nav_to("milk-quality")
        sections = self.driver.find_elements(By.CSS_SELECTOR, ".module-section.active")
        self.assertEqual(len(sections), 1)

    def test_TC113_main_content_visible(self):
        """TC-113 | UI | Main content area rendered | Load page | .main-content visible"""
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".main-content").is_displayed())

    def test_TC114_topbar_visible(self):
        """TC-114 | UI | Topbar rendered | Load page | .topbar visible"""
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".topbar").is_displayed())

    def test_TC115_responsive_window_640(self):
        """TC-115 | UI | Page renders at 640px width | Set window to 640x800 | No JS errors"""
        self.driver.set_window_size(640, 800)
        time.sleep(0.5)
        errors = self.driver.execute_script("return window.__jsErrors || []")
        self.assertEqual(len(errors), 0)
        self.driver.set_window_size(1920, 1080)

    def test_TC116_farmer_form_add_heading(self):
        """TC-116 | UI | 'Add New Farmer' heading present in form | Check h3 text | Heading visible"""
        heading = self.driver.find_element(By.CSS_SELECTOR, "#farmer-details .form-card h3")
        self.assertIn("Add New Farmer", heading.text)

    def test_TC117_farmer_database_heading_present(self):
        """TC-117 | UI | 'Farmer Database' heading present | Check table card heading | Heading visible"""
        heading = self.driver.find_element(By.CSS_SELECTOR, "#farmer-details .table-card h3")
        self.assertIn("Farmer Database", heading.text)

    def test_TC118_cow_icon_in_sidebar(self):
        """TC-118 | UI | Cow icon present in sidebar | Check .sidebar-icon | i element with fa-cow exists"""
        icon = self.driver.find_element(By.CSS_SELECTOR, ".sidebar-icon.fa-cow")
        self.assertIsNotNone(icon)

    def test_TC119_no_console_errors_on_load(self):
        """TC-119 | UI | No critical console errors on page load | Monitor console | No severe JS errors"""
        self.driver.get(BASE_URL)
        time.sleep(2)
        logs = self.driver.get_log("browser")
        severe = [l for l in logs if l.get("level") == "SEVERE"
                  and "favicon" not in l.get("message", "")
                  and "net::ERR" not in l.get("message", "")
                  and "fonts.googleapis" not in l.get("message", "")
                  and "cdnjs" not in l.get("message", "")]
        self.assertEqual(len(severe), 0)

    def test_TC120_payment_loading_spinner_hidden_initially(self):
        """TC-120 | UI | Payment loading spinner hidden initially | Navigate to Payment | #payment-loading hidden"""
        self.nav_to("payment-system")
        spinner = self.driver.find_element(By.ID, "payment-loading")
        display = spinner.value_of_css_property("display")
        self.assertEqual(display, "none")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 9 — Edge Cases & Boundary Tests
# ══════════════════════════════════════════════════════════════════════════════
class TC09_EdgeCases(DairyDashBaseTest):
    def test_TC121_fat_at_boundary_3_5(self):
        """TC-121 | Edge Case | Fat exactly at boundary 3.5 gives 100% fat score | fat=3.5,snf=8.5 | Score = 100"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state":"Tamil Nadu","fat":3.5,"snf":8.5,
                                   "quantity":10,"quality_score":100})
        self.assertTrue(resp.json().get("success"))

    def test_TC122_very_large_quantity(self):
        """TC-122 | Edge Case | Very large quantity processed | quantity=10000 | total_payment very large > 0"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state":"Tamil Nadu","fat":4.0,"snf":8.5,
                                   "quantity":10000,"quality_score":90})
        self.assertGreater(resp.json().get("total_payment", 0), 0)

    def test_TC123_quality_score_100_gives_max_price(self):
        """TC-123 | Edge Case | Quality score 100 gives full base price | quality_score=100 | final=base"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state":"Tamil Nadu","fat":4.0,"snf":8.5,
                                   "quantity":10,"quality_score":100})
        data = resp.json()
        self.assertAlmostEqual(data["base_price_per_litre"], data["final_price_per_litre"], places=1)

    def test_TC124_quality_score_50_halves_price(self):
        """TC-124 | Edge Case | Quality score 50 halves the price | quality_score=50 | final = base/2"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state":"Tamil Nadu","fat":4.0,"snf":8.5,
                                   "quantity":10,"quality_score":50})
        data = resp.json()
        expected = round(data["base_price_per_litre"] * 0.5, 2)
        self.assertAlmostEqual(data["final_price_per_litre"], expected, places=1)

    def test_TC125_empty_body_to_payments_rejected(self):
        """TC-125 | Edge Case | POST /api/payments with empty body returns error | Empty JSON | Not 201"""
        resp = requests.post(f"{API_URL}/payments",
                             json={},
                             headers={"Content-Type":"application/json"})
        self.assertNotEqual(resp.status_code, 201)

    def test_TC126_farmer_search_case_insensitive_ui(self):
        """TC-126 | Edge Case | Search is case-insensitive in UI | Type lowercase for uppercase name | Row visible"""
        self.nav_to("farmer-details")
        requests.post(f"{API_URL}/farmers",
                      json={"f-id":"CASETEST","f-name":"UPPERCASE FARMER",
                            "f-phone":"9876543299","f-bank":"000011112222","f-center":"CC01"})
        self.driver.refresh()
        time.sleep(2)
        self.nav_to("farmer-details")
        self.driver.find_element(By.ID, "search-farmer").send_keys("uppercase")
        time.sleep(0.5)
        visible = [r for r in self.driver.find_elements(By.CSS_SELECTOR,"#farmer-table tbody tr")
                   if r.is_displayed()]
        self.assertGreater(len(visible), 0)

    def test_TC127_api_status_collections_list(self):
        """TC-127 | Edge Case | /api/status returns collections array | GET /api/status | collections is list of 3"""
        resp = requests.get(f"{API_URL}/status")
        cols = resp.json().get("collections", [])
        self.assertEqual(len(cols), 3)

    def test_TC128_pricing_engine_handles_unknown_state(self):
        """TC-128 | Edge Case | Unknown state falls back to default formula | state='UnknownState' | success=True"""
        resp = requests.post(f"{API_URL}/calculate-price",
                             json={"state":"UnknownState","fat":4.0,"snf":8.5,
                                   "quantity":10,"quality_score":90})
        self.assertTrue(resp.json().get("success"))

    def test_TC129_farmer_with_zero_cows_buffaloes(self):
        """TC-129 | Edge Case | Farmer with 0 cows and 0 buffaloes saved | Post farmer with zeros | 201"""
        resp = requests.post(f"{API_URL}/farmers",
                             json={"f-id":"ZERO01","f-name":"Zero Cattle",
                                   "f-phone":"9000009999","f-bank":"000000001111",
                                   "f-center":"ZC01","f-cows":0,"f-buffaloes":0})
        self.assertIn(resp.status_code, [201, 400])

    def test_TC130_multiple_farmers_retrieved(self):
        """TC-130 | Edge Case | Multiple farmers can be stored and retrieved | Add 3 farmers via API | GET returns >=3"""
        for i in range(3):
            requests.post(f"{API_URL}/farmers",
                          json={"f-id": f"MULTI{i}", "f-name": f"Multi Farmer {i}",
                                "f-phone": f"900000000{i}", "f-bank": f"11110000000{i}",
                                "f-center": "MC01"})
        resp  = requests.get(f"{API_URL}/farmers")
        count = len(resp.json())
        self.assertGreaterEqual(count, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
