"""Browser tests with Playwright against the running app (http://localhost:3000).

They use only ZZTEST prospects, which the session fixture imports and later deletes.
"""
import re

import pytest
from playwright.sync_api import Page, expect

from conftest import FRONTEND, sql


@pytest.fixture()
def lead_of(engine):
    def get(pid):
        rows = sql(engine, "SELECT id, status FROM leads WHERE prospect_id = :p", p=pid)
        return rows
    return get


def test_full_workflow_filter_details_save_status_overview_reload(page: Page, test_prospects, lead_of):
    pid = test_prospects["UI1"]
    page.goto(f"{FRONTEND}/prospects")
    page.get_by_role("searchbox", name="Search").fill("ZZTEST UI1")
    row = page.get_by_role("row").filter(has_text="ZZTEST UI1")
    expect(row).to_have_count(1)
    expect(page.get_by_role("row").filter(has_text="ZZTEST UI2")).to_have_count(0)

    row.get_by_role("link", name="ZZTEST UI1").click()
    expect(page).to_have_url(re.compile(f"/prospects/{pid}$"))
    expect(page.get_by_text("Total 80 / 100")).to_be_visible()          # score breakdown matches the API
    expect(page.get_by_text("Unknown: Website is unknown.")).to_be_visible()

    page.get_by_role("button", name="Save as lead").click()
    status = page.get_by_label("Lead status")
    expect(status).to_have_value("new")
    status.select_option("contacted")
    expect(page.get_by_text("Status saved.")).to_be_visible()
    assert lead_of(pid)[0][1] == "contacted"

    page.goto(f"{FRONTEND}/leads?q=ZZTEST+UI1")
    expect(page.get_by_label("Status for ZZTEST UI1").first).to_have_value("contacted")
    page.goto(FRONTEND + "/")
    expect(page.get_by_role("heading", name="Sales dashboard")).to_be_visible()
    expect(page.get_by_role("link", name="Sales dashboard")).to_be_visible()
    page.reload()
    page.goto(f"{FRONTEND}/prospects/{pid}")
    expect(page.get_by_label("Lead status")).to_have_value("contacted")


def test_double_click_save_creates_one_lead(page: Page, test_prospects, lead_of):
    pid = test_prospects["UI2"]
    page.goto(f"{FRONTEND}/prospects/{pid}")
    page.get_by_role("button", name="Save as lead").dblclick()
    expect(page.get_by_label("Lead status")).to_be_visible()
    assert len(lead_of(pid)) == 1


def test_failed_status_update_shows_error_reverts_and_retry_works(page: Page, client, test_prospects, lead_of):
    pid = test_prospects["UI3"]
    client.post(f"/api/v1/prospects/{pid}/save")
    page.goto(f"{FRONTEND}/leads?q=ZZTEST+UI3")
    select = page.get_by_label("Status for ZZTEST UI3").first
    expect(select).to_have_value("new")

    page.route("**/api/v1/leads/*/status", lambda route: route.abort())
    select.select_option("qualified")
    expect(page.get_by_text("The status could not be saved. Try again.").first).to_be_visible()
    expect(select).to_have_value("new")                                  # old value is back
    assert lead_of(pid)[0][1] == "new"                                   # nothing saved

    page.unroute("**/api/v1/leads/*/status")
    select.select_option("qualified")
    expect(page.get_by_text("Status saved.").first).to_be_visible()
    assert lead_of(pid)[0][1] == "qualified"


def test_late_response_does_not_replace_newer_results(page: Page, test_prospects):
    # Delay only the request for the first search, so it arrives after the second one.
    page.add_init_script("""
      const orig = window.fetch;
      window.fetch = async (input, init) => {
        const url = typeof input === 'string' ? input : input.url;
        if (url.includes('/api/v1/prospects?') && url.includes('UI1')) await new Promise(r => setTimeout(r, 2500));
        return orig(input, init);
      };
    """)
    page.goto(f"{FRONTEND}/prospects")
    search = page.get_by_role("searchbox", name="Search")
    search.fill("ZZTEST UI1")
    page.wait_for_timeout(500)                     # past the 300 ms debounce, so the slow request starts
    search.fill("ZZTEST UI2")
    expect(page.get_by_role("row").filter(has_text="ZZTEST UI2")).to_have_count(1)
    page.wait_for_timeout(3000)                    # the slow response has arrived by now
    expect(page.get_by_role("row").filter(has_text="ZZTEST UI1")).to_have_count(0)
    expect(page.get_by_role("row").filter(has_text="ZZTEST UI2")).to_have_count(1)


def test_save_with_keyboard_only(page: Page, test_prospects, lead_of):
    pid = test_prospects["SAVE5"]
    page.goto(f"{FRONTEND}/prospects/{pid}")
    page.get_by_role("button", name="Save as lead").wait_for()
    for _ in range(40):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement && document.activeElement.textContent.trim()") == "Save as lead":
            break
    else:
        pytest.fail("Tab never reached the Save as lead button")
    page.keyboard.press("Enter")
    expect(page.get_by_label("Lead status")).to_be_visible()
    assert len(lead_of(pid)) == 1


@pytest.mark.parametrize("path", ["/", "/prospects", "/leads?q=zztest"])
def test_narrow_screen_has_no_page_level_horizontal_scroll(page: Page, client, test_prospects, path):
    client.post(f"/api/v1/prospects/{test_prospects['SAVE6']}/save")
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(FRONTEND + path)
    page.wait_for_load_state("networkidle")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 1, f"page is {overflow}px wider than the screen"
    if path.startswith("/leads"):
        expect(page.locator("table")).to_be_hidden()                      # cards replace the table
        expect(page.get_by_role("combobox", name="Status for ZZTEST SAVE6").first).to_be_visible()


def test_directory_toggle_filters_and_keeps_the_filter_in_links(page: Page):
    page.goto(f"{FRONTEND}/")
    page.get_by_role("group", name="GAF directory").get_by_role("button", name=re.compile("Commercial")).click()
    expect(page).to_have_url(re.compile(r"directory=commercial"))
    expect(page.get_by_role("link", name="See all").first).to_have_attribute("href", re.compile("directory=commercial"))
    page.goto(f"{FRONTEND}/prospects?directory=commercial")
    expect(page.get_by_text("Commercial listings only")).to_be_visible()
    badges = page.locator("tbody tr td:nth-child(2)")
    expect(badges.first).to_have_text("Commercial")


def test_mark_contacted_is_on_the_lead_page_not_in_the_saved_leads_table(page: Page, client, test_prospects, lead_of):
    pid = test_prospects["UI2"]
    client.post(f"/api/v1/prospects/{pid}/save")
    page.goto(f"{FRONTEND}/leads?q=ZZTEST+UI2")
    expect(page.get_by_role("row").filter(has_text="ZZTEST UI2")).to_have_count(1)
    expect(page.get_by_role("button", name="Mark contacted")).to_have_count(0)

    page.goto(f"{FRONTEND}/prospects/{pid}")
    page.get_by_role("button", name="Mark contacted").click()
    expect(page.get_by_text("Marked as contacted.")).to_be_visible()
    expect(page.get_by_label("Lead status")).to_have_value("contacted")
    expect(page.get_by_role("button", name="Mark contacted")).to_have_count(0)   # only shown for New leads
    assert lead_of(pid)[0][1] == "contacted"
