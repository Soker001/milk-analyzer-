"""
DairyDash Android Application
E2E Appium Test Suite
Covers all layout fragments, forms, DB operations, and UI validations
"""

import unittest
import time
from appium import webdriver
from appium.webdriver.common.appiumby import By
from appium.options.android import UiAutomator2Options

# ── Appium Server Configuration ──────────────────────────────────────────────
APPIUM_PORT = 4723
APPIUM_SERVER_URL = f"http://localhost:{APPIUM_PORT}"

# Global store for test results (for report compiler)
appium_results = []

class AppiumResultCollector(unittest.TestResult):
    """Custom collector to record results for Excel report compiling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_details = []

    def _record(self, test, status, error=None):
        doc = (test.shortDescription() or str(test)).strip()
        parts = [p.strip() for p in doc.split("|")]
        mtc_id = parts[0] if len(parts) > 0 else str(test)
        module = parts[1] if len(parts) > 1 else "General"
        title = parts[2] if len(parts) > 2 else doc
        steps = parts[3] if len(parts) > 3 else ""
        expected = parts[4] if len(parts) > 4 else ""
        actual = "As expected" if status == "PASS" else (str(error).splitlines()[-1] if error else "Failed")
        
        self.test_details.append({
            "tc_id": mtc_id,
            "module": module,
            "title": title,
            "steps": steps,
            "expected": expected,
            "actual": actual,
            "status": status,
            "remarks": "" if status == "PASS" else "Investigate layout / element"
        })
        appium_results.append(self.test_details[-1])

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", err[1])

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "ERROR", err[1])


class DairyDashAppiumBaseTest(unittest.TestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        # Configure desired capabilities using standard UIAutomator2 options
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "Android Emulator"
        options.automation_name = "UiAutomator2"
        options.app = "./app/app/build/outputs/apk/debug/app-debug.apk"
        options.app_package = "com.dairydash"
        options.app_activity = ".MainActivity"
        options.no_reset = False
        
        cls.driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()

    def open_navigation_drawer(self):
        """Click menu/hamburger icon to open navigation drawer."""
        menu_btn = self.driver.find_element(By.ID, "com.dairydash:id/btn_menu")
        menu_btn.click()
        time.sleep(1)

    def select_menu_item(self, text):
        """Select menu item from the navigation drawer."""
        self.open_navigation_drawer()
        item = self.driver.find_element(By.XPATH, f"//android.widget.CheckedTextView[@text='{text}']")
        item.click()
        time.sleep(1)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — App Launch & Sidebar Navigation
# ══════════════════════════════════════════════════════════════════════════════
class MTC01_Navigation(DairyDashAppiumBaseTest):
    def test_MTC001_app_launch_home_screen(self):
        """MTC-001 | Navigation | App launches to home screen | Open DairyDash App | Header title says 'Farmer Details'"""
        title = self.driver.find_element(By.ID, "com.dairydash:id/tv_page_title").text
        self.assertEqual(title, "Farmer Details")

    def test_MTC002_navigation_drawer_opens(self):
        """MTC-002 | Navigation | Drawer opens on click | Click menu button | Navigation View drawer is displayed"""
        self.open_navigation_drawer()
        nav_view = self.driver.find_element(By.ID, "com.dairydash:id/nav_view")
        self.assertTrue(nav_view.is_displayed())
        # Close the drawer
        self.driver.back()

    def test_MTC003_nav_to_milk_quality(self):
        """MTC-003 | Navigation | Navigates to Milk Quality | Open drawer and click 'Milk Quality' | Header title is 'Milk Quality'"""
        self.select_menu_item("Milk Quality")
        title = self.driver.find_element(By.ID, "com.dairydash:id/tv_page_title").text
        self.assertEqual(title, "Milk Quality")

    def test_MTC004_nav_to_adulteration(self):
        """MTC-004 | Navigation | Navigates to Adulteration | Open drawer and click 'Adulteration' | Header title is 'Adulteration'"""
        self.select_menu_item("Adulteration")
        title = self.driver.find_element(By.ID, "com.dairydash:id/tv_page_title").text
        self.assertEqual(title, "Adulteration")

    def test_MTC005_nav_to_payment(self):
        """MTC-005 | Navigation | Navigates to Payment System | Open drawer and click 'Payment System' | Header title is 'Payment System'"""
        self.select_menu_item("Payment System")
        title = self.driver.find_element(By.ID, "com.dairydash:id/tv_page_title").text
        self.assertEqual(title, "Payment System")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — Farmer Details & CRUD Operations
# ══════════════════════════════════════════════════════════════════════════════
class MTC02_FarmerCRUD(DairyDashAppiumBaseTest):
    def setUp(self):
        self.select_menu_item("Farmer Details")

    def test_MTC006_add_valid_farmer(self):
        """MTC-006 | Farmer CRUD | Add new valid farmer | Enter F900, Kumar, 9876543210, save | Farmer row appears in list"""
        self.driver.find_element(By.ID, "com.dairydash:id/et_farmer_id").send_keys("F900")
        self.driver.find_element(By.ID, "com.dairydash:id/et_farmer_name").send_keys("Kumar Swamy")
        self.driver.find_element(By.ID, "com.dairydash:id/et_phone").send_keys("9876543210")
        self.driver.find_element(By.ID, "com.dairydash:id/et_address").send_keys("Village West")
        self.driver.find_element(By.ID, "com.dairydash:id/et_cows").send_keys("4")
        self.driver.find_element(By.ID, "com.dairydash:id/et_buffaloes").send_keys("2")
        self.driver.find_element(By.ID, "com.dairydash:id/et_bank").send_keys("987654321111")
        self.driver.find_element(By.ID, "com.dairydash:id/et_center").send_keys("CTR-90")
        self.driver.find_element(By.ID, "com.dairydash:id/et_supply").send_keys("25")
        
        self.driver.find_element(By.ID, "com.dairydash:id/btn_save_farmer").click()
        time.sleep(1)
        
        # Verify farmer row is added to RecyclerView
        list_text = self.driver.find_element(By.ID, "com.dairydash:id/rv_farmers").text
        self.assertIn("Kumar Swamy", list_text)

    def test_MTC007_search_box_filters_list(self):
        """MTC-007 | Farmer Table | Search filters farmer rows | Type name in search edit text | Only matching name row is visible"""
        search_box = self.driver.find_element(By.ID, "com.dairydash:id/et_search")
        search_box.send_keys("Kumar")
        time.sleep(0.5)
        
        farmers_list = self.driver.find_elements(By.ID, "com.dairydash:id/tv_farmer_name")
        self.assertTrue(len(farmers_list) > 0)
        self.assertEqual(farmers_list[0].text, "Kumar Swamy")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 3 — Milk Quality Analysis
# ══════════════════════════════════════════════════════════════════════════════
class MTC03_MilkQuality(DairyDashAppiumBaseTest):
    def setUp(self):
        self.select_menu_item("Milk Quality")

    def test_MTC008_calculate_quality_score(self):
        """MTC-008 | Milk Quality | Analyze milk quality score | Input qty=10, fat=4.5, snf=9.0 | Base quality score is updated"""
        # Select first farmer in dropdown
        dropdown = self.driver.find_element(By.ID, "com.dairydash:id/spinner_farmer")
        dropdown.click()
        time.sleep(0.5)
        # Select first item in popup
        self.driver.find_element(By.XPATH, "//android.widget.ListView/android.widget.TextView[1]").click()
        
        self.driver.find_element(By.ID, "com.dairydash:id/et_quantity").send_keys("12")
        self.driver.find_element(By.ID, "com.dairydash:id/et_fat").send_keys("4.5")
        self.driver.find_element(By.ID, "com.dairydash:id/et_snf").send_keys("9.0")
        
        self.driver.find_element(By.ID, "com.dairydash:id/btn_analyze").click()
        time.sleep(1)
        
        score_text = self.driver.find_element(By.ID, "com.dairydash:id/tv_score").text
        self.assertEqual(score_text, "100")
        
        status_text = self.driver.find_element(By.ID, "com.dairydash:id/tv_status").text
        self.assertEqual(status_text, "Excellent")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 4 — Adulteration Detection
# ══════════════════════════════════════════════════════════════════════════════
class MTC04_Adulteration(DairyDashAppiumBaseTest):
    def setUp(self):
        self.select_menu_item("Adulteration")

    def test_MTC009_pure_milk_status(self):
        """MTC-009 | Adulteration | Verify Pure Milk score | Water=0, ph=6.6, adulterants=No | Final quality status says 'Pure Milk'"""
        self.driver.find_element(By.ID, "com.dairydash:id/et_water").send_keys("0")
        self.driver.find_element(By.ID, "com.dairydash:id/et_ph").send_keys("6.6")
        
        # Click Generate final score
        self.driver.find_element(By.ID, "com.dairydash:id/btn_generate_score").click()
        time.sleep(1)
        
        status = self.driver.find_element(By.ID, "com.dairydash:id/tv_adulteration_status").text
        self.assertEqual(status, "Pure Milk")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 5 — Payment System
# ══════════════════════════════════════════════════════════════════════════════
class MTC05_Payment(DairyDashAppiumBaseTest):
    def setUp(self):
        self.select_menu_item("Payment System")

    def test_MTC010_calculate_payment_tamil_nadu(self):
        """MTC-010 | Payment | Calculate payout for Tamil Nadu | Select Tamil Nadu and click Calculate | Price result card is displayed"""
        dropdown = self.driver.find_element(By.ID, "com.dairydash:id/spinner_state")
        dropdown.click()
        time.sleep(0.5)
        # Select Tamil Nadu
        self.driver.find_element(By.XPATH, "//android.widget.ListView/android.widget.TextView[@text='Tamil Nadu']").click()
        
        self.driver.find_element(By.ID, "com.dairydash:id/btn_calculate").click()
        time.sleep(2)
        
        total_payment = self.driver.find_element(By.ID, "com.dairydash:id/tv_total").text
        self.assertTrue(total_payment.startswith("₹"))
        
        self.driver.find_element(By.ID, "com.dairydash:id/btn_process_payment").click()
        time.sleep(1)


if __name__ == "__main__":
    unittest.main()
